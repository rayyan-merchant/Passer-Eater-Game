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
        # First, check if indices are out of bounds or invalid
            if (i, j) in visited or i < 0 or i >= self.size or j < 0 or j >= self.size or self.board[i][j] != 'P':
                return False
        # Now safe to check the base case
            if i == self.size - 1:
                return True
            visited.add((i, j))
            return any(dfs(i + di, j + dj) for di, dj in [(1, 0), (0, -1), (0, 1), (1, -1), (1, 1)])

        passer_wins = any(dfs(0, j) for j in range(self.size) if self.board[0][j] == 'P')
        self.passer_win_cache = passer_wins
        return self.passer_win_cache
    
    def check_eater_win(self):
        if self.eater_win_cache is not None:
            return self.eater_win_cache

        for i in range(self.size):
            if all(self.board[i][j] == 'E' for j in range(self.size)): #checks if eater has occupied an entire row
                self.eater_win_cache = True
                return True

        visited = set()
        def dfs(i, j): # Uses DFS to check if the Passer can form a path from the top row to the bottom row using 'P' or empty cells (None).
            if i == self.size - 1:
                return True
            if (i, j) in visited or i < 0 or i >= self.size or j < 0 or j >= self.size or self.board[i][j] == 'E':
                return False
            visited.add((i, j))
            return any(dfs(i + di, j + dj) for di, dj in [(1, 0), (0, -1), (0, 1), (1, -1), (1, 1)])

        can_passer_win = any(dfs(0, j) for j in range(self.size) if self.board[0][j] != 'E')
        self.eater_win_cache = not can_passer_win #The Eater wins if no such path exists (not can_passer_win).
        return self.eater_win_cache

    def find_passer_path(self): #finds the longest path the passer has made (used by the eater to prioritize blocking moves & used in the MCTS sim)
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

    def copy(self): #Creates deep copy of the curr game state. Used in MCTS to simulate moves without modifying the actual game state.
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

    def get_priority_moves(self): #elects a prioritized subset of legal moves for MCTS to explore, improving efficiency.
        legal_moves = self.state.get_legal_moves()
        if not legal_moves:
            return [] #Returns an empty list if there are no legal moves.

        priority_moves = []
        if self.state.current_player == 'E' and self.state.eater_turn_count % 3 == 2: #Priority 1: Overwrite Passer’s Last Move (if allowed)
            last_passer_move = self.state.get_passer_last_move()
            if last_passer_move and last_passer_move in legal_moves:
                priority_moves.append(last_passer_move)

        path, end = self.state.find_passer_path() #Priority 2: Block Passer’s Path
        if end and end[0] < self.state.size and end[1] < self.state.size:
            if (end[0], end[1]) in legal_moves:
                priority_moves.append((end[0], end[1]))
            else:
                for di, dj in [(1, 0), (0, -1), (0, 1), (1, -1), (1, 1)]:
                    ni, nj = end[0] + di, end[1] + dj
                    if 0 <= ni < self.state.size and 0 <= nj < self.state.size and (ni, nj) in legal_moves:
                        priority_moves.append((ni, nj))
                        break

        row_counts = [sum(1 for j in range(self.state.size) if self.state.board[i][j] == 'E') for i in range(self.state.size)] #Priority 3: Places an 'E' in the row with the most 'E' markers to work toward filling a row.
        max_row = row_counts.index(max(row_counts))
        row_moves = [(max_row, j) for j in range(self.state.size) if (max_row, j) in legal_moves]
        if row_moves:
            priority_moves.append(row_moves[0])

        if len(row_counts) > 1:
            second_best_row = sorted(range(len(row_counts)), key=lambda i: row_counts[i], reverse=True)[1] #Priority 4: Places an 'E' in the row with the second-highest number of 'E' markers.
            row_moves = [(second_best_row, j) for j in range(self.state.size) if (second_best_row, j) in legal_moves]
            if row_moves:
                priority_moves.append(row_moves[0])

        empty_moves = [(i, j) for i, j in legal_moves if self.state.board[i][j] is None]
        if empty_moves:
            priority_moves.append(random.choice(empty_moves)) #Priority 5: Adds a random empty cell as a fallback.

        seen = set() #Removes duplicates using a set.
        priority_moves = [move for move in priority_moves if not (move in seen or seen.add(move))]
        return priority_moves if priority_moves else legal_moves[:1] #Falls back to the first legal move if no priority moves are found.

    def is_fully_expanded(self): #Checks if all moves from this node have been explored.
        return len(self.untried_moves) == 0

    def best_child(self, c_param=1.4): #Selects the best child node using the UCB1 formula.
        choices_weights = [
            (child.wins / child.visits) + c_param * math.sqrt((2 * math.log(self.visits) / child.visits)) #
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]

class MCTS:
    def __init__(self, iterations = 500):
        self.iterations = iterations

    def search(self, state): #Runs MCTS to find the best move for the Eater.
        root = MCTSNode(state) #Creates a root node for the current game state.
        for _ in range(self.iterations): #performs iterations






            node = self._select(root) #Selection: Chooses a node to explore (_select).
            if not (node.state.check_passer_win() or node.state.check_eater_win()) and not node.is_fully_expanded():
                node = self._expand(node)  #Expansion: If the node isn’t terminal and has untried moves, expands it (_expand)
            reward = self._simulate(node.state) #Simulation: Simulates a random game from the node’s state (_simulate)
            self._backpropagate(node, reward) #Backpropagation: Updates node statistics (_backpropagate)
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move #Returns the move of the child node with the most visits.

    def _select(self, node): #Moves to the best child (via best_child) until it reaches a terminal state or a node with untried moves.
        while not (node.state.check_passer_win() or node.state.check_eater_win()) and node.is_fully_expanded():
            node = node.best_child()
        return node

    def _expand(self, node): #xpands the node by trying an untried move.
        move = node.untried_moves.pop(0) #Takes the first untried move.
        # #Creates a copy of the state, applies the move, and switches the player.
        new_state = node.state.copy()
        new_state.make_move(move, new_state.current_player)
        new_state.current_player = 'E' if new_state.current_player == 'P' else 'P'
        #Creates a new child node and returns it.
        child_node = MCTSNode(new_state, move, node)
        node.children.append(child_node)
        return child_node

    def _simulate(self, state): #Simulates a game from the given state to estimate the outcome.
        current_state = state.copy()
        max_depth = 5  #sims up to 5 moves
        depth = 0
        while not (current_state.check_passer_win() or current_state.check_eater_win()) and depth < max_depth:
            legal_moves = current_state.get_legal_moves()
            if not legal_moves:
                break
            if current_state.current_player == 'E':
                best_move = None
                best_score = float('-inf')
                for move in legal_moves:
                    i, j = move
                    score = 0
                    current_state.make_move(move, 'E')
                    if current_state.check_eater_win(): #If the move wins for the Eater, assigns an infinite score.
                        score = float('inf')
                    else:
                        row_count = sum(1 for col in range(current_state.size) if current_state.board[i][col] == 'E')
                        score += row_count * 10 #Otherwise, scores based on the number of 'E' markers in the row
                        if current_state.eater_turn_count % 3 == 0 and move == current_state.get_passer_last_move():
                            score += 20 #Adds a bonus (+20) if the move overwrites the Passer’s last move on an overwrite turn.
                    current_state.board[i][j] = None
                    current_state.eater_turn_count -= 1
                    if score > best_score: #Chooses the move with the highest score.
                        best_score = score
                        best_move = move
                current_state.make_move(best_move, 'E') #make the best move
            else:
                # Smarter Passer simulation: extend the longest path
                path, end = current_state.find_passer_path()
                if end and 0 <= end[0] < current_state.size and 0 <= end[1] < current_state.size and (end[0], end[1]) in legal_moves:
                    move = (end[0], end[1])
                else:
                    move_scores = []
                    for move in legal_moves:
                        i, j = move
                        score = 0
                        if i == current_state.size - 1:
                            score += 10
                        move_scores.append((move, score))
                    move = max(move_scores, key=lambda x: x[1])[0]
                current_state.make_move(move, 'P')
            if current_state.current_player == 'P' and current_state.check_passer_win():
                break
            current_state.current_player = 'E' if current_state.current_player == 'P' else 'P'
            depth += 1
        if not (current_state.check_passer_win() or current_state.check_eater_win()): #If no winner after max_depth moves: Computes a heuristic
            max_eater_row = max(sum(1 for j in range(current_state.size) if current_state.board[i][j] == 'E') for i in range(current_state.size))
            passer_path, _ = current_state.find_passer_path()
            passer_path_length = len(passer_path) if passer_path else 0
            # Improved heuristic: balance row-filling and path length
            score = (max_eater_row * 2) - (passer_path_length * 3)
            return 1 if score > 0 else -1
        if current_state.check_passer_win():
            return 1 if state.current_player == 'P' else -1
        return 1 if state.current_player == 'E' else -1

    def _backpropagate(self, node, reward): #Updates the statistics of all nodes from the simulated node to the root.
        while node is not None:
            node.visits += 1
            node.wins += reward
            node = node.parent
            reward = -reward

def cpu_move(game): #Determines the Eater’s move.
    print("Eater is thinking...")
    legal_moves = game.get_legal_moves()
    for move in legal_moves:
        game_copy = game.copy()
        game_copy.make_move(move, 'E')
        if game_copy.check_eater_win():
            print("Eater has chosen its move.")
            return move

    mcts = MCTS(iterations=500)
    move = mcts.search(game)
    print("Eater has chosen its move.")
    return move

def play_game(size):
    game = GameState(size)
    print("Welcome to the Eater game! You are the Passer (P). Connect the top to the bottom with your markers.")
    print("The CPU is the Eater (E) in hard mode using MCTS. It wins by making it impossible for you to connect.")
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
            move = cpu_move(game)
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
    play_game(size)
