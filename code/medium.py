import random
import math


class GameState:
    def __init__(self, size):
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.current_player = 'P'
        self.eater_turn_count = 0  # Track turns for overwrite ability
        self.passer_win_cache = None
        self.eater_win_cache = None
        self.last_move = None
        self.passer_last_move = None

    def get_legal_moves(self):
        if self.current_player == 'P':
            return [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] is None]
        else:
            # Eater can overwrite Passer's cells every 3rd turn
            if self.eater_turn_count % 3 == 2:
                return [(i, j) for i in range(self.size) for j in range(self.size)]
            else:
                return [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] is None]

    def make_move(self, move, player):
        i, j = move
        self.last_move = (move, player)
        self.passer_win_cache = None
        self.eater_win_cache = None
        if player == 'E':
            self.board[i][j] = 'E'
            self.eater_turn_count += 1
        elif player == 'P' and self.board[i][j] is None:
            self.board[i][j] = 'P'
            self.passer_last_move = (i, j)

    def check_passer_win(self):
        # Check if Passer has connected top to bottom
        if self.passer_win_cache is not None:
            return self.passer_win_cache

        visited = set()

        def dfs(i, j):
            if i == self.size - 1 and self.board[i][j] == 'P':
                return True
            if (i, j) in visited or i < 0 or i >= self.size or j < 0 or j >= self.size or self.board[i][j] != 'P':
                return False
            visited.add((i, j))
            return any(dfs(i + di, j + dj) for di, dj in [(1, 0), (0, -1), (0, 1), (1, -1), (1, 1)])

        passer_wins = any(dfs(0, j) for j in range(self.size) if self.board[0][j] == 'P')
        self.passer_win_cache = passer_wins
        return self.passer_win_cache

    def check_eater_win(self):
        # Eater wins by blocking all possible paths or filling a row
        if self.eater_win_cache is not None:
            return self.eater_win_cache

        # Check if Eater has filled a row
        for i in range(self.size):
            if all(self.board[i][j] == 'E' for j in range(self.size)):
                self.eater_win_cache = True
                return True

        visited = set()

        def dfs(i, j):
            # Check if Passer can still connect top to bottom through P or empty cells
            if i == self.size - 1:
                return True
            if (i, j) in visited or i < 0 or i >= self.size or j < 0 or j >= self.size or self.board[i][j] == 'E':
                return False
            visited.add((i, j))
            return any(dfs(i + di, j + dj) for di, dj in [(1, 0), (0, -1), (0, 1), (1, -1), (1, 1)])

        # Eater wins if Passer has no possible path
        can_passer_win = any(dfs(0, j) for j in range(self.size) if self.board[0][j] != 'E')
        self.eater_win_cache = not can_passer_win
        return self.eater_win_cache

    def find_passer_path(self):
        # Find the longest path Passer has made from top row
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
        # Create deep copy of current game state
        new_state = GameState(self.size)
        new_state.board = [row[:] for row in self.board]
        new_state.current_player = self.current_player
        new_state.eater_turn_count = self.eater_turn_count
        new_state.passer_win_cache = self.passer_win_cache
        new_state.eater_win_cache = self.eater_win_cache
        new_state.last_move = self.last_move
        new_state.passer_last_move = self.passer_last_move
        return new_state


class MiniMaxPlayer:
    def __init__(self, max_depth=3):
        self.max_depth = max_depth

    def get_move(self, game_state):
        print("Eater is thinking using Minimax...")
        legal_moves = game_state.get_legal_moves()

        # Check for immediate winning moves first
        for move in legal_moves:
            game_copy = game_state.copy()
            game_copy.make_move(move, 'E')
            if game_copy.check_eater_win():
                print("Eater found a winning move!")
                return move

        # Use minimax with alpha-beta pruning
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')

        prioritized_moves = self.prioritize_moves(game_state, legal_moves)

        for move in prioritized_moves:
            game_copy = game_state.copy()
            game_copy.make_move(move, 'E')
            game_copy.current_player = 'P'

            score = self.minimax(game_copy, 0, False, alpha, beta)

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)

        print("Eater has chosen its move.")
        return best_move

    def prioritize_moves(self, state, legal_moves):
        # Sort moves by potential value to improve alpha-beta pruning
        move_scores = []

        # Prioritize overwrite moves on Passer's last move
        if state.eater_turn_count % 3 == 2:
            last_passer_move = state.get_passer_last_move()
            if last_passer_move and last_passer_move in legal_moves:
                move_scores.append((last_passer_move, 1000))

        # Prioritize moves along Passer's path
        path, _ = state.find_passer_path()
        for move in legal_moves:
            if move in path:
                move_scores.append((move, 500))

        # Score remaining moves based on heuristics
        for move in legal_moves:
            if any(m[0] == move for m in move_scores):
                continue

            row, col = move
            # Prefer middle positions
            central_score = (state.size // 2 - abs(row - state.size // 2)) + (
                    state.size // 2 - abs(col - state.size // 2))
            # Prefer rows with existing Eater pieces
            row_eater_count = sum(1 for j in range(state.size) if state.board[row][j] == 'E')

            score = row_eater_count * 10 + central_score
            move_scores.append((move, score))

        # Sort moves by score (highest first)
        prioritized_moves = [move for move, score in sorted(move_scores, key=lambda x: x[1], reverse=True)]

        # Add any remaining legal moves
        for move in legal_moves:
            if move not in prioritized_moves:
                prioritized_moves.append(move)

        return prioritized_moves

    def minimax(self, state, depth, is_maximizing, alpha, beta):
        # Terminal conditions
        if state.check_eater_win():
            return 1000 - depth  # Prefer quicker wins
        elif state.check_passer_win():
            return -1000 + depth  # Prefer slower losses
        elif depth >= self.max_depth:
            return self.evaluate_board(state)

        legal_moves = state.get_legal_moves()
        if not legal_moves:
            return 0

        if is_maximizing:  # Eater's turn (maximize)
            max_eval = float('-inf')
            for move in legal_moves:
                new_state = state.copy()
                new_state.make_move(move, 'E')
                new_state.current_player = 'P'
                eval_score = self.minimax(new_state, depth + 1, False, alpha, beta)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:  # Passer's turn (minimize)
            min_eval = float('inf')
            for move in legal_moves:
                new_state = state.copy()
                new_state.make_move(move, 'P')
                new_state.current_player = 'E'
                eval_score = self.minimax(new_state, depth + 1, True, alpha, beta)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval

    def evaluate_board(self, state):
        # Heuristic evaluation - positive favors Eater, negative favors Passer
        # Check for nearly completed rows (good for Eater)
        row_scores = 0
        for i in range(state.size):
            eater_count = sum(1 for j in range(state.size) if state.board[i][j] == 'E')
            if eater_count == state.size:
                return 900  # Almost win
            row_scores += (eater_count * eater_count) / state.size  # Square for emphasis

        # Calculate Passer's path progress
        path, end = state.find_passer_path()
        path_length = len(path) if path else 0
        path_progress = 0
        if path and end and end[0] >= 0 and end[0] < state.size:
            path_progress = end[0] / (state.size - 1)  # How far down the path goes (0 to 1)

        # Calculate connectivity metric for Passer
        connectivity = self.calculate_connectivity(state)

        # Check for blockage potential
        blockage = self.calculate_blockage(state)

        # Combine metrics
        eater_score = row_scores + blockage
        passer_score = path_length * 10 + path_progress * 50 + connectivity * 15

        return eater_score - passer_score

    def calculate_connectivity(self, state):
        # Measure how connected Passer's pieces are
        connectivity = 0
        for i in range(state.size):
            for j in range(state.size):
                if state.board[i][j] == 'P':
                    adjacent_count = 0
                    for di, dj in [(1, 0), (0, -1), (0, 1), (1, -1), (1, 1)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < state.size and 0 <= nj < state.size and state.board[ni][nj] == 'P':
                            adjacent_count += 1
                    connectivity += adjacent_count
        return connectivity

    def calculate_blockage(self, state):
        # Calculate how effectively Eater is blocking potential paths
        blockage = 0
        middle_start = state.size // 3
        middle_end = 2 * state.size // 3

        for i in range(middle_start, middle_end + 1):
            eater_count = sum(1 for j in range(state.size) if state.board[i][j] == 'E')
            blockage += eater_count * 5

        # Extra points for blocking the middle column
        middle_col = state.size // 2
        middle_blockage = sum(5 for i in range(state.size) if state.board[i][middle_col] == 'E')
        blockage += middle_blockage

        return blockage


def cpu_move(game, difficulty="medium"):
    print(f"Eater is thinking in {difficulty} mode...")
    legal_moves = game.get_legal_moves()

    # Check for immediate win first
    for move in legal_moves:
        game_copy = game.copy()
        game_copy.make_move(move, 'E')
        if game_copy.check_eater_win():
            print("Eater found a winning move!")
            return move

    minimax_depth = 3
    minimax_player = MiniMaxPlayer(max_depth=minimax_depth)
    move = minimax_player.get_move(game)

    print("Eater has chosen its move.")
    return move


def play_game(size, difficulty="medium"):
    game = GameState(size)
    print("Welcome to the Eater game! You are the Passer (P). Connect the top to the bottom with your markers.")
    print(
        f"The CPU is the Eater (E) in {difficulty} mode using Minimax. It wins by making it impossible for you to connect.")
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
    play_game(size, difficulty="medium")