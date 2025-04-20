import pygame
import sys
import random
from collections import deque
import heapq

pygame.init()

WIDTH, HEIGHT = 720, 800
ROWS, COLS = 9, 9
SQUARE_SIZE = WIDTH // COLS

EMPTY =0
EATER =-1
PASSER =1

# Color modes
LIGHT_MODE = {
    'BG': (245, 245, 245),
    'LINE': (220, 220, 220),
    'EATER': (255, 30, 30),#red
    'PASSER': (218,165,32),#yellow
    'TEXT': (20, 20, 20),
    'BORDER_H': (218,165,32),#yellow
    'BORDER_V': (255, 30, 30),#red
    'GLOW': (180, 180, 180)
}

DARK_MODE = {
    'BG': (18,18,24),
    'LINE': (30, 30, 30),
    'EATER': (128,0,0), #red
    'PASSER': (75,61,156), #puprple
    'TEXT': (230, 230, 230),
    'BORDER_H': (75,61,156),#purple acc to dark theme display
    'BORDER_V': (139,0,0),#red ask if white needed
    'GLOW': (60, 60, 60)
}

# Screen and font setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Passer-Eater")
font_large = pygame.font.SysFont("Rubik Mono One", 50)
font_medium = pygame.font.SysFont("Rubik Mono One", 54)

# Game state
PAUSED = False
theme = DARK_MODE


def draw_ui_bar():
    #pygame.draw.rect(screen, theme['BG'], (0, 0, WIDTH, 80))
    #pygame.draw.rect(screen, theme['LINE'], (0, 0, WIDTH, 80), border_radius=8)
    title = font_large.render("PASSER-EATER", True, theme['TEXT'])
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))


def draw_glow_circle(surface, color, center, radius):
    glow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    for i in range(radius, 0, -4):
        alpha = int((i / radius) * 80)
        pygame.draw.circle(glow_surface, (*color, alpha), (radius * 2, radius * 2), i)
    surface.blit(glow_surface, (center[0] - radius * 2, center[1] - radius * 2))


# def draw_board(board):
#     screen.fill(theme['BG'])

#     for row in range(ROWS):
#         for col in range(COLS):
#             rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE + 80, SQUARE_SIZE, SQUARE_SIZE)
#             pygame.draw.rect(screen, theme['LINE'], rect, border_radius=8)

#             center = rect.center
#             if board[row][col] == EATER:
#                 draw_glow_circle(screen, theme['EATER'], center, SQUARE_SIZE // 3 + 8)
#                 pygame.draw.circle(screen, theme['EATER'], center, SQUARE_SIZE // 3)
#             elif board[row][col] == PASSER:
#                 draw_glow_circle(screen, theme['PASSER'], center, SQUARE_SIZE // 3 + 8)
#                 pygame.draw.circle(screen, theme['PASSER'], center, SQUARE_SIZE // 3)

#     # Borders
#     pygame.draw.line(screen, theme['BORDER_H'], (0, 80), (WIDTH, 80), 6)
#     pygame.draw.line(screen, theme['BORDER_H'], (0, HEIGHT - 1), (WIDTH, HEIGHT - 1), 6)
#     pygame.draw.line(screen, theme['BORDER_V'], (0, 80), (0, HEIGHT), 6)
#     pygame.draw.line(screen, theme['BORDER_V'], (WIDTH - 1, 80), (WIDTH - 1, HEIGHT), 6)

#     draw_ui_bar()
#     pygame.display.flip()
def draw_light_effects():
    light_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    center = (WIDTH // 2, HEIGHT // 2)
    for radius in range(300, 0, -40):
        alpha = max(0, 60 - radius // 5)
        pygame.draw.circle(light_surface, (255, 255, 255, alpha), center, radius)
    screen.blit(light_surface, (0, 0))
def draw_board(board):
    screen.fill(theme['BG'])

    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE + 80, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, theme['LINE'], rect, 1)  # Grid lines for clarity
            
            center=rect.center    
            if board[row][col] == EATER:
                draw_glow_circle(screen, theme['EATER'], center, SQUARE_SIZE // 3 + 8)
                pygame.draw.circle(screen, theme['EATER'], center, SQUARE_SIZE // 3)
            elif board[row][col] == PASSER:
                draw_glow_circle(screen, theme['PASSER'], center, SQUARE_SIZE // 3 + 8)
                pygame.draw.circle(screen, theme['PASSER'], center, SQUARE_SIZE // 3)


    # Draw borders
    pygame.draw.line(screen, theme['BORDER_H'], (0, 80), (WIDTH, 80), 10)
    pygame.draw.line(screen, theme['BORDER_H'], (0, HEIGHT - 1), (WIDTH, HEIGHT - 1), 15)
    pygame.draw.line(screen, theme['BORDER_V'], (0, 80), (0, HEIGHT), 10)
    pygame.draw.line(screen, theme['BORDER_V'], (WIDTH - 1, 80), (WIDTH - 1, HEIGHT), 10)

    draw_ui_bar()
    pygame.display.flip()

def get_row_col_from_pos(pos):
    x, y = pos
    row = (y - 80) // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col


def toggle_theme():
    global theme
    theme = DARK_MODE if theme == LIGHT_MODE else LIGHT_MODE


def main():
    global PAUSED
    board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
    draw_board(board)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    PAUSED = not PAUSED
                elif event.key == pygame.K_t:
                    toggle_theme()
                    draw_board(board)
            elif not PAUSED and event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_pos(pos)
                if 0 <= row < ROWS and 0 <= col < COLS and board[row][col] == EMPTY:
                    board[row][col] = PASSER
                    draw_board(board)

        draw_board(board)



main()

