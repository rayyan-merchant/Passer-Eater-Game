import pygame
import sys
import random
from collections import deque
import heapq

# Game constants
EMPTY = 0
EATER = -1
PASSER = 1

# Color modes
LIGHT_MODE = {
    'BG': (245, 245, 245),
    'LINE': (220, 220, 220),
    'EATER': (255, 30, 30),  # red
    'PASSER': (218, 165, 32),  # yellow
    'TEXT': (20, 20, 20),
    'BORDER_H': (218, 165, 32),  # yellow
    'BORDER_V': (255, 30, 30),  # red
    'GLOW': (180, 180, 180)
}

DARK_MODE = {
    'BG': (18, 18, 24),
    'LINE': (30, 30, 30),
    'EATER': (128, 0, 0),  # red
    'PASSER': (75, 61, 156),  # purple
    'TEXT': (230, 230, 230),
    'BORDER_H': (75, 61, 156),  # purple acc to dark theme display
    'BORDER_V': (139, 0, 0),  # red
    'GLOW': (60, 60, 60)
}


class PasserEaterGame:
    def __init__(self, width=720, height=800, rows=9, cols=9, is_dark_mode=True):
        self.WIDTH = width
        self.HEIGHT = height
        self.ROWS = rows
        self.COLS = cols
        self.SQUARE_SIZE = self.WIDTH // self.COLS
        self.PAUSED = False
        self.theme = DARK_MODE if is_dark_mode else LIGHT_MODE

        # Initialize the board
        self.board = [[EMPTY for _ in range(self.COLS)] for _ in range(self.ROWS)]

        # Initialize pygame if it's not already initialized
        if not pygame.get_init():
            pygame.init()

        # Create screen
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Passer-Eater")

        # Initialize fonts
        self.font_large = pygame.font.SysFont("Rubik Mono One", 50)
        self.font_medium = pygame.font.SysFont("Rubik Mono One", 54)

    def draw_ui_bar(self):
        title = self.font_large.render("PASSER-EATER", True, self.theme['TEXT'])
        self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 20))

    def draw_glow_circle(self, surface, color, center, radius):
        glow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        for i in range(radius, 0, -4):
            alpha = int((i / radius) * 80)
            pygame.draw.circle(glow_surface, (*color, alpha), (radius * 2, radius * 2), i)
        surface.blit(glow_surface, (center[0] - radius * 2, center[1] - radius * 2))

    def draw_light_effects(self):
        light_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        center = (self.WIDTH // 2, self.HEIGHT // 2)
        for radius in range(300, 0, -40):
            alpha = max(0, 60 - radius // 5)
            pygame.draw.circle(light_surface, (255, 255, 255, alpha), center, radius)
        self.screen.blit(light_surface, (0, 0))

    def draw_board(self):
        self.screen.fill(self.theme['BG'])

        for row in range(self.ROWS):
            for col in range(self.COLS):
                rect = pygame.Rect(col * self.SQUARE_SIZE, row * self.SQUARE_SIZE + 80,
                                   self.SQUARE_SIZE, self.SQUARE_SIZE)
                pygame.draw.rect(self.screen, self.theme['LINE'], rect, 1)  # Grid lines

                center = rect.center
                if self.board[row][col] == EATER:
                    self.draw_glow_circle(self.screen, self.theme['EATER'], center, self.SQUARE_SIZE // 3 + 8)
                    pygame.draw.circle(self.screen, self.theme['EATER'], center, self.SQUARE_SIZE // 3)
                elif self.board[row][col] == PASSER:
                    self.draw_glow_circle(self.screen, self.theme['PASSER'], center, self.SQUARE_SIZE // 3 + 8)
                    pygame.draw.circle(self.screen, self.theme['PASSER'], center, self.SQUARE_SIZE // 3)

        # Draw borders
        pygame.draw.line(self.screen, self.theme['BORDER_H'], (0, 80), (self.WIDTH, 80), 10)
        pygame.draw.line(self.screen, self.theme['BORDER_H'], (0, self.HEIGHT - 1), (self.WIDTH, self.HEIGHT - 1), 15)
        pygame.draw.line(self.screen, self.theme['BORDER_V'], (0, 80), (0, self.HEIGHT), 10)
        pygame.draw.line(self.screen, self.theme['BORDER_V'], (self.WIDTH - 1, 80), (self.WIDTH - 1, self.HEIGHT), 10)

        self.draw_ui_bar()
        pygame.display.flip()

    def get_row_col_from_pos(self, pos):
        x, y = pos
        row = (y - 80) // self.SQUARE_SIZE
        col = x // self.SQUARE_SIZE
        return row, col

    def toggle_theme(self):
        self.theme = DARK_MODE if self.theme == LIGHT_MODE else LIGHT_MODE
        self.draw_board()

    def place_piece(self, row, col, piece_type):
        """Place a piece on the board at the specified position"""
        if 0 <= row < self.ROWS and 0 <= col < self.COLS:
            self.board[row][col] = piece_type
            self.draw_board()
            return True
        return False

    def is_valid_move(self, row, col):
        """Check if a move to the given position is valid"""
        return 0 <= row < self.ROWS and 0 <= col < self.COLS and self.board[row][col] == EMPTY

    def reset_game(self):
        """Reset the game board"""
        self.board = [[EMPTY for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.draw_board()

    def run_game_loop(self):
        """Run the main game loop"""
        self.draw_board()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.PAUSED = not self.PAUSED
                    elif event.key == pygame.K_t:
                        self.toggle_theme()
                elif not self.PAUSED and event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = self.get_row_col_from_pos(pos)
                    if self.is_valid_move(row, col):
                        self.place_piece(row, col, PASSER)

            # Redraw the board each frame
            self.draw_board()


# This allows the file to be run directly or imported
if __name__ == "__main__":
    game = PasserEaterGame()
    game.run_game_loop()
