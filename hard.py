import random
import math

class GameState:
    def __init__(self, size):
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]  # None: empty, 'P': Passer, 'E': Eater
        self.current_player = 'P'  # Passer starts
        self.eater_turn_count = 0  # Track Eater's turns for overwrite restriction
        self.passer_win_cache = None  # Cache for Passer win condition
        self.eater_win_cache = None  # Cache for Eater win condition
        self.last_move = None  # Track last move to invalidate cache
        self.passer_last_move = None  # Track Passer's last move

    def get_legal_moves(self):
        if self.current_player == 'P':
            return [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] is None]
        else:  # Eater
            if self.eater_turn_count % 3 == 2:  # Overwrite allowed every 3 turns (turns 3, 6, 9, ...)
                return [(i, j) for i in range(self.size) for j in range(self.size)]
            else:  # Other turns: must place in empty cell
                return [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] is None]

    def make_move(self, move, player):
        i, j = move
        self.last_move = (move, player)  # Invalidate cache on move
        self.passer_win_cache = None
        self.eater_win_cache = None
        if player == 'E':
            self.board[i][j] = 'E'
            self.eater_turn_count += 1
        elif player == 'P' and self.board[i][j] is None:
            self.board[i][j] = 'P'
            self.passer_last_move = (i, j)  # Update Passer's last move

    def check_passer_win(self):
        if self.passer_win_cache is not None:
            return self.passer_win_cache

        visited = set()
        def dfs(i, j):
            if i == self.size - 1 and self.board[i][j] == 'P':  # Reached bottom row with a 'P'
                return True
            if (i, j) in visited or i < 0 or i >= self.size or j < 0 or j >= self.size or self.board[i][j] != 'P':
                return False
            visited.add((i, j))
            return any(dfs(i + di, j + dj) for di, dj in [(1, 0), (0, -1), (0, 1), (1, -1), (1, 1)])

        passer_wins = any(dfs(0, j) for j in range(self.size) if self.board[0][j] == 'P')
        self.passer_win_cache = passer_wins
        return self.passer_win_cache

    def check_eater_win(self):
        if self.eater_win_cache is not None:
            return self.eater_win_cache

        for i in range(self.size):
            if all(self.board[i][j] == 'E' for j in range(self.size)):
                self.eater_win_cache = True
                return True

        visited = set()
        def dfs(i, j):
            if i == self.size - 1:
                return True
            if (i, j) in visited or i < 0 or i >= self.size or j < 0 or j >= self.size or self.board[i][j] == 'E':
                return False
            visited.add((i, j))
            return any(dfs(i + di, j + dj) for di, dj in [(1, 0), (0, -1), (0, 1), (1, -1), (1, 1)])

        can_passer_win = any(dfs(0, j) for j in range(self.size) if self.board[0][j] != 'E')
        self.eater_win_cache = not can_passer_win
        return self.eater_win_cache

    def find_passer_path(self):
        best_path = []
        best_length = 0
        best_end = None

        for start_col in range(self.size):
            if self.board[0][start_col] != 'P':
                continue
            visited = set()
            path = [(0, start_col)]
            def dfs(i, j):
                nonlocal path, best_path, best_length, best_end
                if (i, j) in visited or i < 0 or i >= self.size or j < 0 or j >= self.size or self.board[i][j] != 'P':
                    if len(path) > best_length:
                        best_length = len(path)
                        best_path = path[:]
                        best_end = (i, j)
                    return
                visited.add((i, j))
                for di, dj in [(1, 0), (0, -1), (0, 1), (1, -1), (1, 1)]:
                    path.append((i + di, j + dj))
                    dfs(i + di, j + dj)
                    path.pop()

            dfs(0, start_col)

        return best_path, best_end

    def display(self):
        print('   ', ' '.join(str(i + 1) for i in range(self.size)))
        for i in range(self.size):
            row = [self.board[i][j] if self.board[i][j] else '|' for j in range(self.size)]
            print(f'{i + 1:2} ', ' '.join(row))

    def get_passer_last_move(self):
        return self.passer_last_move

    def copy(self):
        new_state = GameState(self.size)
        new_state.board = [row[:] for row in self.board]
        new_state.current_player = self.current_player
        new_state.eater_turn_count = self.eater_turn_count
        new_state.passer_win_cache = self.passer_win_cache
        new_state.eater_win_cache = self.eater_win_cache
        new_state.last_move = self.last_move
        new_state.passer_last_move = self.passer_last_move
        return new_state

class MCTSNode:
    def __init__(self, state, move=None, parent=None):
        self.state = state
        self.move = move
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = self.get_priority_moves()

    def get_priority_moves(self):
        legal_moves = self.state.get_legal_moves()
        if not legal_moves:
            return []

        priority_moves = []
        # Priority 1: Overwrite Passer's last move (if allowed)
        if self.state.current_player == 'E' and self.state.eater_turn_count % 3 == 2:
            last_passer_move = self.state.get_passer_last_move()
            if last_passer_move and last_passer_move in legal_moves:
                priority_moves.append(last_passer_move)

        # Priority 2: Block Passer's path
        path, end = self.state.find_passer_path()
        if end and end[0] < self.state.size and end[1] < self.state.size:
            if (end[0], end[1]) in legal_moves:
                priority_moves.append((end[0], end[1]))
            else:
                for di, dj in [(1, 0), (0, -1), (0, 1), (1, -1), (1, 1)]:
                    ni, nj = end[0] + di, end[1] + dj
                    if 0 <= ni < self.state.size and 0 <= nj < self.state.size and (ni, nj) in legal_moves:
                        priority_moves.append((ni, nj))
                        break

        # Priority 3: Predictive blocking - moves near Passer's last move
        if self.state.current_player == 'E' and self.state.get_passer_last_move():
            last_i, last_j = self.state.get_passer_last_move()
            for di, dj in [(1, 0), (0, -1), (0, 1), (1, -1), (1, 1)]:
                ni, nj = last_i + di, last_j + dj
                if 0 <= ni < self.state.size and 0 <= nj < self.state.size and (ni, nj) in legal_moves:
                    priority_moves.append((ni, nj))

        # Priority 4: Place 'E' in row with most 'E' markers
        row_counts = [sum(1 for j in range(self.state.size) if self.state.board[i][j] == 'E') for i in range(self.state.size)]
        max_row = row_counts.index(max(row_counts))
        row_moves = [(max_row, j) for j in range(self.state.size) if (max_row, j) in legal_moves]
        if row_moves:
            priority_moves.append(row_moves[0])

        # Priority 5: Place 'E' in row with second-highest number of 'E' markers
        if len(row_counts) > 1:
            second_best_row = sorted(range(len(row_counts)), key=lambda i: row_counts[i], reverse=True)[1]
            row_moves = [(second_best_row, j) for j in range(self.state.size) if (second_best_row, j) in legal_moves]
            if row_moves:
                priority_moves.append(row_moves[0])

        # Priority 6: Random empty cell as fallback
        empty_moves = [(i, j) for i, j in legal_moves if self.state.board[i][j] is None]
        if empty_moves:
            priority_moves.append(random.choice(empty_moves))

        seen = set()
        priority_moves = [move for move in priority_moves if not (move in seen or seen.add(move))]
        return priority_moves if priority_moves else legal_moves[:1]

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, c_param=1.4):
        choices_weights = [
            (child.wins / child.visits) + c_param * math.sqrt((2 * math.log(self.visits) / child.visits))
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]

class MCTS:
    def __init__(self, iterations=1000, max_depth=8):
        self.iterations = iterations
        self.max_depth = max_depth

    def search(self, state):
        root = MCTSNode(state)
        for _ in range(self.iterations):
            node = self._select(root)
            if not (node.state.check_passer_win() or node.state.check_eater_win()) and not node.is_fully_expanded():
                node = self._expand(node)
            reward = self._simulate(node.state)
            self._backpropagate(node, reward)
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move

    def _select(self, node):
        while not (node.state.check_passer_win() or node.state.check_eater_win()) and node.is_fully_expanded():
            node = node.best_child()
        return node

    def _expand(self, node):
        move = node.untried_moves.pop(0)
        new_state = node.state.copy()
        new_state.make_move(move, new_state.current_player)
        new_state.current_player = 'E' if new_state.current_player == 'P' else 'P'
        child_node = MCTSNode(new_state, move, node)
        node.children.append(child_node)
        return child_node

    def _simulate(self, state):
        current_state = state.copy()
        depth = 0
        while not (current_state.check_passer_win() or current_state.check_eater_win()) and depth < self.max_depth:
            legal_moves = current_state.get_legal_moves()
            if not legal_moves:
                break
            if current_state.current_player == 'P':
                # Smarter Passer simulation: extend the longest path
                path, end = current_state.find_passer_path()
                move = None
                if end and 0 <= end[0] < current_state.size and 0 <= end[1] < current_state.size and (end[0], end[1]) in legal_moves:
                    move = (end[0], end[1])
                else:
                    move_scores = []
                    for m in legal_moves:
                        i, j = m
                        score = 0
                        if i == current_state.size - 1:
                            score += 10
                        move_scores.append((m, score))
                    move = max(move_scores, key=lambda x: x[1])[0]
                current_state.make_move(move, 'P')
            else:
                # Eater tries to maximize Passer's path length
                best_move = max(legal_moves, key=lambda move: self._score_move_for_eater(current_state, move))
                current_state.make_move(best_move, 'E')
            if current_state.current_player == 'P' and current_state.check_passer_win():
                break
            current_state.current_player = 'E' if current_state.current_player == 'P' else 'P'
            depth += 1

        if current_state.check_passer_win():
            return -1  # Bad for Eater
        elif current_state.check_eater_win():
            return 1  # Good for Eater
        else:
            # Heuristic: Maximize Passer's path length
            path_length = self._find_passer_path_length(current_state)
            return 1.0 / (path_length + 1) if path_length != float('inf') else 0

    def _score_move_for_eater(self, state, move):
        temp_state = state.copy()
        temp_state.make_move(move, 'E')
        path_length = self._find_passer_path_length(temp_state)
        score = path_length if path_length != float('inf') else 1000
        # Bonus for overwrite moves
        if state.eater_turn_count % 3 == 0 and state.board[move[0]][move[1]] == 'P':
            # Additional bonus if overwriting a cell in the Passer's path
            path, _ = state.find_passer_path()
            if move in path:
                score += 100
            else:
                score += 50
        # Predictive blocking: Bonus for moves near Passer's last move
        if state.get_passer_last_move():
            last_i, last_j = state.get_passer_last_move()
            move_i, move_j = move
            distance = abs(last_i - move_i) + abs(last_j - move_j)
            if distance <= 2:
                score += 20 / (distance + 1)
        return score

    def _find_passer_path_length(self, state):
        path, _ = state.find_passer_path()
        if not path:
            return float('inf')
        # Estimate remaining distance to bottom
        if path:
            last_pos = path[-1]
            remaining_distance = state.size - 1 - last_pos[0]
            return len(path) + remaining_distance
        return float('inf')

    def _backpropagate(self, node, reward):
        while node is not None:
            node.visits += 1
            node.wins += reward
            node = node.parent
            reward = -reward

def cpu_move(game, difficulty="hard"):
    print("Eater is thinking...")
    legal_moves = game.get_legal_moves()
    for move in legal_moves:
        game_copy = game.copy()
        game_copy.make_move(move, 'E')
        if game_copy.check_eater_win():
            print("Eater has chosen its move.")
            return move

    # Adjust MCTS parameters based on difficulty
    if difficulty == "hard":
        iterations = 1000
        max_depth = 8
    elif difficulty == "medium":
        iterations = 500
        max_depth = 5
    else:
        iterations = 200
        max_depth = 3
    mcts = MCTS(iterations=iterations, max_depth=max_depth)
    move = mcts.search(game)
    print("Eater has chosen its move.")
    return move

def play_game(size, difficulty="hard"):
    game = GameState(size)
    print("Welcome to the Eater game! You are the Passer (P). Connect the top to the bottom with your markers.")
    print(f"The CPU is the Eater (E) in {difficulty} mode using MCTS. It wins by making it impossible for you to connect.")
    print("Paths can move down, left, right, down-left, or down-right (no upward movement).")
    print("Eater can overwrite your markers every 3 turns (turns 3, 6, 9, ...).")
    print("Enter your move as 'row col' (e.g., '1 1'). Type 'exit' to quit.")
    game_over = False
    while not game_over:
        game.display()
        if game.current_player == 'P':
            while True:
                try:
                    print("Passer's turn (row col, or 'exit' to quit): ")
                    user_input = input().strip()
                    if user_input.lower() == 'exit':
                        print("Game exited.")
                        return
                    row, col = map(int, user_input.split())
                    move = (row - 1, col - 1)
                    if move in game.get_legal_moves():
                        break
                    else:
                        print("Invalid move! Cell must be empty. Try again.")
                except EOFError:
                    print("\nInput stream closed. Exiting game.")
                    return
                except (ValueError, IndexError):
                    print("Invalid input! Enter two numbers (row col) or 'exit'. Try again.")
            print("Passer making move...")
            game.make_move(move, 'P')
            if game.check_passer_win():
                game.display()
                print("Passer wins by forming a connected path of P markers!")
                game_over = True
            else:
                game.current_player = 'E'
        else:
            # Display overwrite warning
            if game.eater_turn_count % 3 == 2:
                print("Warning: Eater can overwrite a 'P' marker on this turn!")
            move = cpu_move(game, difficulty)
            if move is None:
                print("No legal moves for Eater. Passer wins by default!")
                game_over = True
                break
            game.make_move(move, 'E')
            print(f"Eater (CPU) plays at {move[0] + 1} {move[1] + 1}")
            if game.check_eater_win():
                game.display()
                print("Eater wins by blocking all possible paths!")
                game_over = True
            else:
                game.current_player = 'P'

if __name__ == "__main__":
    size = 9
    play_game(size, difficulty="hard")