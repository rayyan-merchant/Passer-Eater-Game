import pygame
import random
from game import PasserEaterGame, PASSER, EATER, EMPTY

def easy_mode(player_name, is_dark_mode=True):
    # Initialize the game
    game = PasserEaterGame(is_dark_mode=is_dark_mode)

    # Set up initial positions
    # Passer starts at top-left (0, 0)
    game.place_piece(0, 0, PASSER)
    # Eater starts at bottom-right (ROWS-1, COLS-1)
    game.place_piece(game.ROWS - 1, game.COLS - 1, EATER)

    # Track current positions
    passer_pos = [0, 0]
    eater_pos = [game.ROWS - 1, game.COLS - 1]

    # Game state
    current_player = PASSER  # Passer goes first
    game_over = False
    winner = None

    # Main game loop
    game.draw_board()

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            # Handle player moves when it's their turn
            if current_player == PASSER and event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = game.get_row_col_from_pos(pos)

                # Check if valid move (only right or down for Passer)
                if ((row == passer_pos[0] + 1 and col == passer_pos[1]) or  # Down
                        (row == passer_pos[0] and col == passer_pos[1] + 1)):  # Right

                    if game.is_valid_move(row, col):
                        # Clear old position
                        game.board[passer_pos[0]][passer_pos[1]] = EMPTY

                        # Update position
                        passer_pos = [row, col]
                        game.place_piece(row, col, PASSER)

                        # Check if Passer reached bottom row (win condition)
                        if row == game.ROWS - 1:
                            game_over = True
                            winner = PASSER
                        else:
                            current_player = EATER  # Switch turns

        # AI's turn (easy mode = random valid move)
        if current_player == EATER and not game_over:
            pygame.time.delay(500)  # Add delay to make AI moves visible

            # Get possible moves (left or up)
            possible_moves = []

            # Check up move
            if eater_pos[0] > 0 and game.board[eater_pos[0] - 1][eater_pos[1]] != EATER:
                possible_moves.append([eater_pos[0] - 1, eater_pos[1]])

            # Check left move
            if eater_pos[1] > 0 and game.board[eater_pos[0]][eater_pos[1] - 1] != EATER:
                possible_moves.append([eater_pos[0], eater_pos[1] - 1])

            if possible_moves:
                # Choose a random move for easy difficulty
                new_pos = random.choice(possible_moves)

                # Clear old position
                game.board[eater_pos[0]][eater_pos[1]] = EMPTY

                # Check if Eater captured Passer
                if new_pos[0] == passer_pos[0] and new_pos[1] == passer_pos[1]:
                    game_over = True
                    winner = EATER

                # Update position
                eater_pos = new_pos
                game.place_piece(new_pos[0], new_pos[1], EATER)

                # Switch turns if not game over
                if not game_over:
                    current_player = PASSER

        game.draw_board()

        # Display winner if game is over
        if game_over:
            winner_text = f"{player_name} wins!" if winner == PASSER else "AI wins!"
            winner_surface = game.font_medium.render(winner_text, True, game.theme['TEXT'])
            game.screen.blit(winner_surface, (game.WIDTH // 2 - winner_surface.get_width() // 2,
                                          game.HEIGHT // 2 - winner_surface.get_height() // 2))
            pygame.display.flip()

            # Wait for a moment before returning to menu
            pygame.time.delay(3000)
            return winner

    return None