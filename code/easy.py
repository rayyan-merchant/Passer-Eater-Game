import random

class GameState:
    def __init__(self, size):
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.current_player = 'P'
        self.eater_turn_count = 0
        self.passer_win_cache = None
        self.eater_win_cache = None
        self.last_move = None
        self.passer_last_move = None


    # Get list of legal moves for the current player
    def get_legal_moves(self):
        if self.current_player == 'P':
            # Passer can only move to empty cells
            return [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] is None]
        else:
            # Eater can overwrite every third turn
            if self.eater_turn_count % 3 == 2:
                return [(i, j) for i in range(self.size) for j in range(self.size)]
            else:
                return [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] is None]

    def make_move(self, move, player):    # Apply a move to the board
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

    def check_passer_win(self):  # Check if Passer has connected top to bottom
        if self.passer_win_cache is not None:
            return self.passer_win_cache

        visited = set()
        def dfs(i, j):
            if (i, j) in visited or i < 0 or i >= self.size or j < 0 or j >= self.size or self.board[i][j] != 'P':
                return False
            if i == self.size - 1:
                return True
            visited.add((i, j))
            return any(dfs(i + di, j + dj) for di, dj in [(1, 0), (0, -1), (0, 1), (1, -1), (1, 1)])

        passer_wins = any(dfs(0, j) for j in range(self.size) if self.board[0][j] == 'P')
        self.passer_win_cache = passer_wins
        return self.passer_win_cache

    def check_eater_win(self):  # Check if Eater has won (either a full row or Passer can't win anymore)
        if self.eater_win_cache is not None:
            return self.eater_win_cache

        # Check for any full row
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

        # Eater wins if Passer cannot reach the bottom
        can_passer_win = any(dfs(0, j) for j in range(self.size) if self.board[0][j] != 'E')
        self.eater_win_cache = not can_passer_win
        return self.eater_win_cache

    def display(self):
        print('   ', ' '.join(str(i + 1) for i in range(self.size)))
        for i in range(self.size):
            row = [self.board[i][j] if self.board[i][j] else '|' for j in range(self.size)]
            print(f'{i + 1:2} ', ' '.join(row))

    def copy(self):  # Create a deep copy of the current game state
        new_state = GameState(self.size)
        new_state.board = [row[:] for row in self.board]
        new_state.current_player = self.current_player
        new_state.eater_turn_count = self.eater_turn_count
        new_state.passer_win_cache = self.passer_win_cache
        new_state.eater_win_cache = self.eater_win_cache
        new_state.last_move = self.last_move
        new_state.passer_last_move = self.passer_last_move
        return new_state

def cpu_move_easy(game):
    print("Eater is thinking...")

    size = game.size
    board = game.board
    legal_moves = game.get_legal_moves()
    overwrite_allowed = game.eater_turn_count % 3 == 2

    if not legal_moves:
        return None

    # Overwrite any random Passer move if allowed
    if overwrite_allowed:
        passer_cells = [(r, c) for r in range(size) for c in range(size) if board[r][c] == 'P']
        if passer_cells:
            move = random.choice(passer_cells)
            print("Eater is overwriting a random Passer marker!")
            return move

    # Smarter blocking logic
    score_map = {}
    for r in range(size):
        for c in range(size):
            if board[r][c] == 'P':
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < size and 0 <= nc < size and (nr, nc) in legal_moves:
                        score = nr
                        nearby = sum(
                            1 for ddr, ddc in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                            if 0 <= nr + ddr < size and 0 <= nc + ddc < size and board[nr + ddr][nc + ddc] == 'P'
                        )
                        score += nearby * 2
                        score_map[(nr, nc)] = max(score_map.get((nr, nc), 0), score)

    if score_map:
        move = max(score_map.items(), key=lambda x: x[1])[0]
    else:
        move = random.choice(legal_moves)

    print(f"Eater plays at {move[0] + 1} {move[1] + 1}")
    return move

def play_game(size):
    game = GameState(size)
    print("Welcome to the Eater game! You are the Passer (P). Connect the top to the bottom with your markers.")
    print("The CPU is the Eater (E) in easy mode. It wins by making it impossible for you to connect.")
    print("Eater may play next to your markers or randomly on the board.")
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
                        print("Invalid move! Try again.")
                except EOFError:
                    print("\nInput stream closed. Exiting game.")
                    return
                except (ValueError, IndexError):
                    print("Invalid input! Enter two numbers (row col) or 'exit'. Try again.")
            game.make_move(move, 'P')
            if game.check_passer_win():
                game.display()
                print("Passer wins by forming a connected path!")
                game_over = True
            else:
                game.current_player = 'E'
        else:
            move = cpu_move_easy(game)
            if move is None:
                print("No legal moves for Eater. Passer wins by default!")
                game_over = True
                break
            game.make_move(move, 'E')
            if game.check_eater_win():
                game.display()
                print("Eater wins by blocking all possible paths!")
                game_over = True
            else:
                game.current_player = 'P'

if __name__ == "__main__":
    size = 9
    play_game(size)
