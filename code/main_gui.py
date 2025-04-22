import pygame
import sys
from easy import easy_mode
# from medium import medium_mode
from hard import play_game  # Import play_game directly
import math
import random

pygame.init()

WIDTH, HEIGHT = 1000, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PASSER EATER")

# Use relative paths assuming main.py is in the 'code' folder
FONT_T = pygame.font.Font(r'font/RubikMonoOne-Regular.ttf', 36)
FONT = pygame.font.Font(r"font/RubikMonoOne-Regular.ttf", 32)
FONT2 = pygame.font.Font(r"font/RubikMonoOne-Regular.ttf", 15)
INPUT_FONT = pygame.font.Font(r"font/RubikMonoOne-Regular.ttf", 24)

# Light Mode Colors
LIGHT_BG_COLOR = (255, 255, 255)
LIGHT_TEXT_COLOR = (0, 0, 0)
LIGHT_BUTTON_COLOR = (255, 223, 186)
LIGHT_HOVER_COLOR = (255, 183, 77)
LIGHT_INPUT_BG = (240, 240, 240)
LIGHT_INPUT_ACTIVE = (220, 220, 220)

# Dark Mode Colors
DARK_BG_COLOR = (6, 22, 57) #deep blue
DARK_TEXT_COLOR = (245, 245, 245)
DARK_BUTTON_COLOR = (72, 61, 139)
DARK_HOVER_COLOR = (123, 104, 238)
DARK_INPUT_BG = (40, 42, 54)
DARK_INPUT_ACTIVE = (60, 62, 74)

# Start Screen Colors
START_BG_COLOR = (6, 22, 57)  # Deep blue
START_ACCENT_COLOR = (48, 180, 255)  # Bright blue
START_TITLE_COLOR = (255, 204, 0)  # Gold
START_TEXT_COLOR = (255, 255, 255)  # White
EATER_COLOR = (139,0,0)  # Green
PASSER_COLORS = [(75, 61, 156), (51, 187, 255), (255, 204, 68), (255, 68, 204)]  # Orange, Blue, Yellow, Pink

# Initial Mode is Dark
is_dark_mode = True

# Menu states
MENU_START_SCREEN = -1  # New state for the starting screen
MENU_MAIN = 0
MENU_GAME_TYPE = 1
MENU_HUMAN_VS_HUMAN_INPUT = 2
MENU_HUMAN_VS_AI_INPUT = 3
MENU_AI_DIFFICULTY = 4
MENU_HUMAN_VS_HUMAN_DIFFICULTY = 5
current_menu = MENU_START_SCREEN  # Start with the start screen

# Player names
player1_name = ""
player2_name = ""
ai_player_name = "AI"
human_player_name = ""
active_input = None

# Difficulties
ai_difficulty = None
human_vs_human_difficulty = None

# Define image variables as None initially
sun_img = None
moon_img = None
has_images = False

# Load sun and moon images with relative paths
try:
    sun_img = pygame.image.load(r"code\sunn.png").convert_alpha()
    moon_img = pygame.image.load(r"code\moon.webp").convert_alpha()
    sun_img = pygame.transform.scale(sun_img, (30, 30))
    moon_img = pygame.transform.scale(moon_img, (30, 30))
    has_images = True
except Exception as e:
    print(f"Image files not found, using text symbols instead: {e}")

# Star class for the start screen
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(0.5, 2)
        self.opacity = random.uniform(0.5, 1)

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), int(self.size))

# Passer class for the start screen
class Passer:
    def __init__(self):
        self.color = random.choice(PASSER_COLORS)
        self.x = random.randint(WIDTH // 4, 3 * WIDTH // 4)
        self.y = random.randint(HEIGHT // 4, 3 * HEIGHT // 4)
        self.size = random.randint(10, 25)
        self.direction = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.5, 2)

    def move(self):
        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed

        # Bounce off edges
        if self.x < 0 or self.x > WIDTH:
            self.direction = math.pi - self.direction
        if self.y < 0 or self.y > HEIGHT:
            self.direction = -self.direction

    def draw(self, surface):
        # Body
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        # Eyes
        eye_size = max(2, self.size // 5)
        pygame.draw.circle(surface, (255, 255, 255),
                          (int(self.x - self.size // 3), int(self.y - self.size // 4)), eye_size)
        pygame.draw.circle(surface, (255, 255, 255),
                          (int(self.x + self.size // 3), int(self.y - self.size // 4)), eye_size)
        # Smile
        smile_rect = pygame.Rect(self.x - self.size // 2, self.y + self.size // 4, self.size, self.size // 2)
        pygame.draw.arc(surface, (255, 255, 255), smile_rect, 0, math.pi, 2)

# Eater class for the start screen
class Eater:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.size = 60
        self.mouth_angle = 0
        self.mouth_direction = 1
        self.target = None
        self.eaten = []

    def set_target(self, passers):
        if not passers or random.random() < 0.01:  # Sometimes change target randomly
            self.target = None

        if self.target is None and passers:
            self.target = random.choice(passers)

    def move(self, passers):
        if self.target in passers:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist > 2:
                self.x += dx / dist * 1.5
                self.y += dy / dist * 1.5

            # Check for collision/eating
            if dist < self.size / 2:
                if self.target in passers:
                    self.eaten.append(self.target)
                    passers.remove(self.target)
                self.target = None
        else:
            self.target = None

        # # Animate mouth
        # self.mouth_angle += 0.05 * self.mouth_direction
        # if self.mouth_angle > 0.3 or self.mouth_angle < 0:
        #     self.mouth_direction *= -1

    def draw(self, surface):
    # Solid round body
        pygame.draw.ellipse(surface, EATER_COLOR, (self.x - self.size / 2, self.y - self.size / 2, self.size, self.size))

    # Eye direction (points at target if there is one)
        eye_offset_x = 0
        eye_offset_y = -10

        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            angle = math.atan2(dy, dx)
            eye_offset_x = 15 * math.cos(angle)
            eye_offset_y = 15 * math.sin(angle)

        eye_x = self.x + eye_offset_x
        eye_y = self.y + eye_offset_y

    # Big central eye
        pygame.draw.circle(surface, (255, 255, 255), (int(eye_x), int(eye_y)), 12)  # Eye white
        pygame.draw.circle(surface, (0, 0, 0), (int(eye_x), int(eye_y)), 6)         # Pupil

# Button Class
class Button:
    def __init__(self, text, x, y, width, height, callback, image=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.callback = callback
        self.image = image

    def draw(self, surface, button_color, hover_color, text_color):
        mouse_pos = pygame.mouse.get_pos()
        color = hover_color if self.rect.collidepoint(mouse_pos) else button_color
        pygame.draw.rect(surface, color, self.rect, border_radius=15)

        if self.image and has_images:
            img_rect = self.image.get_rect(center=self.rect.center)
            surface.blit(self.image, img_rect)
        else:
            text_surf = FONT.render(self.text, True, text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

# Input Box Class
class InputBox:
    def __init__(self, x, y, width, height, label="", text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.label = label
        self.active = False

    def handle_event(self, event):
        global active_input
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                active_input = self
            else:
                self.active = False

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                active_input = None
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 15 and (event.unicode.isalnum() or event.unicode == " "):
                    self.text += event.unicode
        return False

    def draw(self, surface, bg_color, active_color, text_color):
        label_surface = FONT2.render(self.label, True, text_color)
        surface.blit(label_surface, (self.rect.x, self.rect.y - 30))
        pygame.draw.rect(surface, active_color if self.active else bg_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, text_color, self.rect, 2, border_radius=10)
        text_surface = INPUT_FONT.render(self.text, True, text_color)
        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))
        if self.active and pygame.time.get_ticks() % 1000 < 500:
            text_width = INPUT_FONT.size(self.text)[0]
            cursor_pos = self.rect.x + 10 + text_width
            pygame.draw.line(surface, text_color, (cursor_pos, self.rect.y + 10),
                             (cursor_pos, self.rect.y + self.rect.height - 10), 2)

# Button Callbacks
def show_main_menu():
    global current_menu
    current_menu = MENU_MAIN

def show_game_selection():
    global current_menu
    current_menu = MENU_GAME_TYPE

def back_to_main():
    global current_menu
    current_menu = MENU_MAIN

def back_to_game_selection():
    global current_menu
    current_menu = MENU_GAME_TYPE

def back_to_difficulty_selection():
    global current_menu
    current_menu = MENU_HUMAN_VS_HUMAN_DIFFICULTY

def show_human_vs_human_input():
    global current_menu
    current_menu = MENU_HUMAN_VS_HUMAN_DIFFICULTY  # First go to difficulty selection

def show_human_vs_human_difficulty():
    global current_menu
    current_menu = MENU_HUMAN_VS_HUMAN_DIFFICULTY

def show_human_vs_human_names():
    global current_menu, player1_name, player2_name, active_input
    current_menu = MENU_HUMAN_VS_HUMAN_INPUT
    player1_name = ""
    player2_name = ""
    active_input = None

def show_ai_difficulty_selection():
    global current_menu
    current_menu = MENU_AI_DIFFICULTY

def set_ai_difficulty(difficulty):
    global ai_difficulty, current_menu
    ai_difficulty = difficulty
    show_human_vs_ai_input()

def set_human_vs_human_difficulty(difficulty):
    global human_vs_human_difficulty, current_menu
    human_vs_human_difficulty = difficulty
    show_human_vs_human_names()  # Transition to name input after difficulty selection

def show_human_vs_ai_input():
    global current_menu, human_player_name, active_input
    current_menu = MENU_HUMAN_VS_AI_INPUT
    human_player_name = ""
    active_input = None

def start_human_vs_human_game():
    if player1_name.strip() and player2_name.strip():
        print(f"Starting Human vs Human game with players: {player1_name} and {player2_name} on {human_vs_human_difficulty} difficulty")
        if human_vs_human_difficulty == "Easy":
            print("Loading easy_mode")
            easy_mode()
        elif human_vs_human_difficulty == "Medium":
            print("Loading medium_mode")
            # medium_mode()
        elif human_vs_human_difficulty == "Hard":
            print("Loading hard_mode")
            play_game(9)  # Call play_game from hard.py with size=9
    else:
        print("Please enter names for both players")

def start_human_vs_ai_game():
    if human_player_name.strip():
        print(f"Starting Human vs AI game with player: {human_player_name} against AI on {ai_difficulty} difficulty")
        if ai_difficulty == "Easy":
            print("Loading easy_mode")
            easy_mode()
        elif ai_difficulty == "Medium":
            print("Loading medium_mode")
            # medium_mode()
        elif ai_difficulty == "Hard":
            print("Loading hard_mode")
            play_game(9)  # Call play_game from hard.py with size=9
    else:
        print("Please enter your name")

def show_instructions():
    running = True
    while running:
        bg_color = DARK_BG_COLOR if is_dark_mode else LIGHT_BG_COLOR
        text_color = DARK_TEXT_COLOR if is_dark_mode else LIGHT_TEXT_COLOR
        button_color = DARK_BUTTON_COLOR if is_dark_mode else LIGHT_BUTTON_COLOR
        hover_color = DARK_HOVER_COLOR if is_dark_mode else LIGHT_HOVER_COLOR

        SCREEN.fill(bg_color)
        instructions = [
            "GAME INSTRUCTIONS",
            "",
            "Overview:",
            "A simple 2-player board game played on an M x M grid.",
            "Player 1 is the Passer. Player 2 is the Eater.",
            "",
            "Objective:",
            "- Passer must reach the last row (bottom) of the grid.",
            "- Eater must capture the Passer before they reach it.",
            "",
            "Passer Rules:",
            "- Starts at top-left cell (0, 0).",
            "- Can move one step: RIGHT or DOWN only.",
            "",
            "Eater Rules:",
            "- Starts at bottom-right cell (M-1, M-1).",
            "- Can move one step: LEFT or UP only.",
            "",
            "Winning Conditions:",
            "- Passer wins by reaching any cell in the bottom row first.",
            "- Eater wins by landing on the same cell as the Passer first.",
            "",
            "Notes:",
            "- No diagonal moves are allowed.",
            "- The grid is empty (no obstacles).",
            "- Game ends immediately when a player wins.",
            "",
            "Click       to return to the main menu."
        ]
        y = 25
        for line in instructions:
            text_surface = FONT2.render(line, True, text_color)
            SCREEN.blit(text_surface, (30, y))
            y += 20
        back_button = pygame.Rect(100, 560, 80, 30)
        mouse_pos = pygame.mouse.get_pos()
        back_color = hover_color if back_button.collidepoint(mouse_pos) else button_color
        pygame.draw.rect(SCREEN, back_color, back_button, border_radius=5)
        back_text = FONT2.render("Back", True, text_color)
        SCREEN.blit(back_text, (back_button.x + 15, back_button.y + 5))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    running = False

def toggle_mode():
    global is_dark_mode
    is_dark_mode = not is_dark_mode

# Create start screen elements
stars = [Star() for _ in range(100)]
passers = [Passer() for _ in range(5)]
eater = Eater()
start_button = Button("PRESS START", WIDTH//2 - 150, HEIGHT - 150, 300, 60, show_main_menu)

# Main Menu Buttons - Centered
main_menu_buttons = [
    Button("Start Game", WIDTH//2 - 300, 200, 600, 80, show_game_selection),
    Button("Instructions", WIDTH//2 - 300, 320, 600, 80, show_instructions),
]

# Game Type Selection Buttons - Centered
game_type_buttons = [
    Button("Player vs Player", WIDTH//2 - 300, 200, 600, 80, show_human_vs_human_input),
    Button("Player vs AI", WIDTH//2 - 300, 320, 600, 80, show_ai_difficulty_selection),
    Button("Back", WIDTH//2 - 300, 440, 600, 80, back_to_main),
]

# Difficulty Selection Buttons for AI - Centered
difficulty_buttons_ai = [
    Button("Easy", WIDTH//2 - 300, 160, 600, 80, lambda: set_ai_difficulty("Easy")),
    Button("Medium", WIDTH//2 - 300, 260, 600, 80, lambda: set_ai_difficulty("Medium")),
    Button("Hard", WIDTH//2 - 300, 360, 600, 80, lambda: set_ai_difficulty("Hard")),
    Button("Back", WIDTH//2 - 300, 460, 600, 80, back_to_game_selection),
]

# Difficulty Selection Buttons for Human vs Human - Centered
difficulty_buttons_human = [
    Button("Easy", WIDTH//2 - 300, 160, 600, 80, lambda: set_human_vs_human_difficulty("Easy")),
    Button("Medium", WIDTH//2 - 300, 260, 600, 80, lambda: set_human_vs_human_difficulty("Medium")),
    Button("Hard", WIDTH//2 - 300, 360, 600, 80, lambda: set_human_vs_human_difficulty("Hard")),
    Button("Back", WIDTH//2 - 300, 460, 600, 80, back_to_game_selection),  # Updated to go back to game type selection
]

# Input boxes and buttons for Human vs Human - Centered
player1_input = InputBox(WIDTH//2 - 250, 200, 500, 50, "Enter Player 1 (Passer) Name:")
player2_input = InputBox(WIDTH//2 - 250, 300, 500, 50, "Enter Player 2 (Eater) Name:")
human_vs_human_start_button = Button("Start Game", WIDTH//2 - 150, 400, 300, 60, start_human_vs_human_game)
human_vs_human_back_button = Button("Back", WIDTH//2 - 150, 480, 300, 60, back_to_difficulty_selection)  # Updated to go back to difficulty selection

# Input box and buttons for Human vs AI - Centered
human_player_input = InputBox(WIDTH//2 - 250, 250, 500, 50, "Enter Your Name:")
human_vs_ai_start_button = Button("Start Game", WIDTH//2 - 150, 350, 300, 60, start_human_vs_ai_game)
human_vs_ai_back_button = Button("Back", WIDTH//2 - 150, 430, 300, 60, show_ai_difficulty_selection)

# Draw the start screen
# def draw_start_screen():
#     # Fill background
#     SCREEN.fill(START_BG_COLOR)

#     # Draw border
#     pygame.draw.rect(SCREEN, START_ACCENT_COLOR, pygame.Rect(10, 10, WIDTH - 20, HEIGHT - 20), 3, 15)

#     # Draw stars
#     for star in stars:
#         star.draw(SCREEN)

#     # Draw passers
#     for passer in passers:
#         passer.draw(SCREEN)
#         passer.move()

#     # Update eater
#     eater.set_target(passers)
#     eater.move(passers)
#     eater.draw(SCREEN)

#     # Spawn new passers if too few
#     if len(passers) < 3 and random.random() < 0.02:
#         passers.append(Passer())

#     # Draw title
#     title_font = pygame.font.Font(r"font/RubikMonoOne-Regular.ttf", 72)
#     title_text = title_font.render("PASSER-EATER", True, START_TITLE_COLOR)
#     title_shadow = title_font.render("PASSER-EATER", True, (255, 54, 102))

#     # Shadow/glow effect
#     title_rect = title_text.get_rect(center=(WIDTH // 2 + 4, 120 + 4))
#     SCREEN.blit(title_shadow, title_rect)

#     # Main title
#     title_rect = title_text.get_rect(center=(WIDTH // 2, 120))
#     SCREEN.blit(title_text, title_rect)

#     # # Game tagline
#     # tagline_font = pygame.font.Font(r"font/RubikMonoOne-Regular.ttf", 24)
#     # tagline_text = tagline_font.render("EAT PASSERS  ••• GAIN POINTS  ••• SURVIVE", True, START_ACCENT_COLOR)
#     # tagline_rect = tagline_text.get_rect(center=(WIDTH // 2, 470))
#     # SCREEN.blit(tagline_text, tagline_rect)

#     # # High score display - Centered
#     # score_rect = pygame.Rect(WIDTH // 2 - 120, 500, 240, 40)
#     # pygame.draw.rect(SCREEN, START_BG_COLOR, score_rect, 0, 10)
#     # pygame.draw.rect(SCREEN, START_ACCENT_COLOR, score_rect, 2, 10)
#     # score_font = pygame.font.Font(r"font/RubikMonoOne-Regular.ttf", 20)
#     # score_text = score_font.render("HIGH SCORE: 4200", True, START_ACCENT_COLOR)
#     # score_text_rect = score_text.get_rect(center=(WIDTH // 2, 520))
#     # SCREEN.blit(score_text, score_text_rect)

#     # # Draw start button with pulsing effect
#     # pulse = (math.sin(pygame.time.get_ticks() * 0.003) + 1) * 0.5
#     # pulse_color = (
#     #     int(START_ACCENT_COLOR[0] * pulse + START_TITLE_COLOR[0] * (1 - pulse)),
#     #     int(START_ACCENT_COLOR[1] * pulse + START_TITLE_COLOR[1] * (1 - pulse)),
#     #     int(START_ACCENT_COLOR[2] * pulse + START_TITLE_COLOR[2] * (1 - pulse))
#     # )
#     # start_button.draw(SCREEN, START_BG_COLOR, pulse_color, START_TEXT_COLOR)
# # Tagline - shifted upward a bit
#     tagline_font = pygame.font.Font(r"font/RubikMonoOne-Regular.ttf", 24)
#     tagline_text = tagline_font.render("EAT PASSERS  •••  GAIN POINTS  •••  SURVIVE", True, START_ACCENT_COLOR)
#     tagline_rect = tagline_text.get_rect(center=(WIDTH // 2, 400))  # was 470
#     SCREEN.blit(tagline_text, tagline_rect)

# # Start button - safely below tagline
#     start_button_y = tagline_rect.bottom + 30  # 30px space below tagline

#     pulse = (math.sin(pygame.time.get_ticks() * 0.003) + 1) * 0.5
#     pulse_color = (
#         int(START_ACCENT_COLOR[0] * pulse + START_TITLE_COLOR[0] * (1 - pulse)),
#         int(START_ACCENT_COLOR[1] * pulse + START_TITLE_COLOR[1] * (1 - pulse)),
#         int(START_ACCENT_COLOR[2] * pulse + START_TITLE_COLOR[2] * (1 - pulse))
# )
#     start_button.draw(SCREEN, START_BG_COLOR, pulse_color, START_TEXT_COLOR, y_override=start_button_y)

# # High score - moved to top-left corner
#     score_font = pygame.font.Font(r"font/RubikMonoOne-Regular.ttf", 20)
#     score_text = score_font.render("HIGH SCORE: 4200", True, START_ACCENT_COLOR)
#     score_text_rect = score_text.get_rect(topleft=(20, 20))  # top-left corner with padding
#     SCREEN.blit(score_text, score_text_rect)
def draw_start_screen():
    # Fill background
    SCREEN.fill(START_BG_COLOR)

    # Draw border
    pygame.draw.rect(SCREEN, START_ACCENT_COLOR, pygame.Rect(10, 10, WIDTH - 20, HEIGHT - 20), 3, 15)

    # Draw stars
    for star in stars:
        star.draw(SCREEN)

    # Draw passers
    for passer in passers:
        passer.draw(SCREEN)
        passer.move()

    # Update eater
    eater.set_target(passers)
    eater.move(passers)
    eater.draw(SCREEN)

    # Spawn new passers if too few
    if len(passers) < 3 and random.random() < 0.02:
        passers.append(Passer())

    # Title with glow
    title_font = pygame.font.Font(r"font/RubikMonoOne-Regular.ttf", 72)
    title_text = title_font.render("PASSER-EATER", True, START_TITLE_COLOR)
    title_shadow = title_font.render("PASSER-EATER", True, (255, 54, 102))

    title_rect = title_text.get_rect(center=(WIDTH // 2 + 4, 120 + 4))
    SCREEN.blit(title_shadow, title_rect)
    title_rect = title_text.get_rect(center=(WIDTH // 2, 120))
    SCREEN.blit(title_text, title_rect)

    # Tagline - positioned a bit higher
    tagline_font = pygame.font.Font(r"font/RubikMonoOne-Regular.ttf", 24)
    tagline_text = tagline_font.render("EAT PASSERS  •••  GAIN POINTS  •••  SURVIVE", True, START_ACCENT_COLOR)
    tagline_rect = tagline_text.get_rect(center=(WIDTH // 2, 400))
    SCREEN.blit(tagline_text, tagline_rect)

    # Move start button below tagline
    start_button.rect.y = tagline_rect.bottom + 30

    # Pulsing effect
    pulse = (math.sin(pygame.time.get_ticks() * 0.003) + 1) * 0.5
    pulse_color = (
        int(START_ACCENT_COLOR[0] * pulse + START_TITLE_COLOR[0] * (1 - pulse)),
        int(START_ACCENT_COLOR[1] * pulse + START_TITLE_COLOR[1] * (1 - pulse)),
        int(START_ACCENT_COLOR[2] * pulse + START_TITLE_COLOR[2] * (1 - pulse))
    )
    start_button.draw(SCREEN, START_BG_COLOR, pulse_color, START_TEXT_COLOR)

    # High score - placed in top-left corner
    score_font = pygame.font.Font(r"font/RubikMonoOne-Regular.ttf", 20)
    score_text = score_font.render("HIGH SCORE: 4200", True, START_ACCENT_COLOR)
    score_text_rect = score_text.get_rect(topleft=(20, 20))
    SCREEN.blit(score_text, score_text_rect)

# Main Game Loop
def main_menu():
    global is_dark_mode, current_menu, player1_name, player2_name, human_player_name, active_input
    mode_button_img = moon_img if is_dark_mode else sun_img if has_images else None
    mode_button = Button("☀️" if not is_dark_mode else "🌙", 930, 20, 50, 50, toggle_mode, mode_button_img)
    clock = pygame.time.Clock()

    while True:
        bg_color = DARK_BG_COLOR if is_dark_mode else LIGHT_BG_COLOR
        text_color = DARK_TEXT_COLOR if is_dark_mode else LIGHT_TEXT_COLOR
        button_color = DARK_BUTTON_COLOR if is_dark_mode else LIGHT_BUTTON_COLOR
        hover_color = DARK_HOVER_COLOR if is_dark_mode else LIGHT_HOVER_COLOR
        input_bg = DARK_INPUT_BG if is_dark_mode else LIGHT_INPUT_BG
        input_active = DARK_INPUT_ACTIVE if is_dark_mode else LIGHT_INPUT_ACTIVE

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle start screen events separately
            if current_menu == MENU_START_SCREEN:
                start_button.check_click(event)
                # Skip other event handling for start screen
                continue

            mode_button.check_click(event)
            if current_menu == MENU_MAIN:
                for button in main_menu_buttons:
                    button.check_click(event)
            elif current_menu == MENU_GAME_TYPE:
                for button in game_type_buttons:
                    button.check_click(event)
            elif current_menu == MENU_AI_DIFFICULTY:
                for button in difficulty_buttons_ai:
                    button.check_click(event)
            elif current_menu == MENU_HUMAN_VS_HUMAN_INPUT:
                if player1_input.handle_event(event):
                    player1_name = player1_input.text
                    active_input = player2_input
                    player2_input.active = True
                if player2_input.handle_event(event):
                    player2_name = player2_input.text
                    active_input = None
                human_vs_human_start_button.check_click(event)
                human_vs_human_back_button.check_click(event)
            elif current_menu == MENU_HUMAN_VS_HUMAN_DIFFICULTY:
                for button in difficulty_buttons_human:
                    button.check_click(event)
            elif current_menu == MENU_HUMAN_VS_AI_INPUT:
                if human_player_input.handle_event(event):
                    human_player_name = human_player_input.text
                    active_input = None
                human_vs_ai_start_button.check_click(event)
                human_vs_ai_back_button.check_click(event)

        # Render appropriate screen based on current_menu
        if current_menu == MENU_START_SCREEN:
            draw_start_screen()
        else:
            SCREEN.fill(bg_color)

            if current_menu == MENU_MAIN:
                line1 = FONT_T.render("WELCOME TO", True, text_color)
                line2 = FONT_T.render("PASSER EATER, CHAMP!", True, text_color)
                rect1 = line1.get_rect(center=(SCREEN.get_width() // 2, 50))
                rect2 = line2.get_rect(center=(SCREEN.get_width() // 2, 100))
                SCREEN.blit(line1, rect1)
                SCREEN.blit(line2, rect2)
                for button in main_menu_buttons:
                    button.draw(SCREEN, button_color, hover_color, text_color)
            elif current_menu == MENU_GAME_TYPE:
                select_text = FONT.render("SELECT GAME MODE", True, text_color)
                select_rect = select_text.get_rect(center=(SCREEN.get_width() // 2, 100))
                SCREEN.blit(select_text, select_rect)
                for button in game_type_buttons:
                    button.draw(SCREEN, button_color, hover_color, text_color)
            elif current_menu == MENU_AI_DIFFICULTY:
                diff_text = FONT.render("SELECT DIFFICULTY", True, text_color)
                diff_rect = diff_text.get_rect(center=(SCREEN.get_width() // 2, 100))
                SCREEN.blit(diff_text, diff_rect)
                for button in difficulty_buttons_ai:
                    button.draw(SCREEN, button_color, hover_color, text_color)
            elif current_menu == MENU_HUMAN_VS_HUMAN_INPUT:
                title_text = FONT.render("ENTER PLAYER NAMES", True, text_color)
                title_rect = title_text.get_rect(center=(SCREEN.get_width() // 2, 100))
                SCREEN.blit(title_text, title_rect)
                player1_input.draw(SCREEN, input_bg, input_active, text_color)
                player2_input.draw(SCREEN, input_bg, input_active, text_color)
                human_vs_human_start_button.draw(SCREEN, button_color, hover_color, text_color)
                human_vs_human_back_button.draw(SCREEN, button_color, hover_color, text_color)
            elif current_menu == MENU_HUMAN_VS_HUMAN_DIFFICULTY:
                diff_text = FONT.render("SELECT DIFFICULTY", True, text_color)
                diff_rect = diff_text.get_rect(center=(SCREEN.get_width() // 2, 100))
                SCREEN.blit(diff_text, diff_rect)
                for button in difficulty_buttons_human:
                    button.draw(SCREEN, button_color, hover_color, text_color)
            elif current_menu == MENU_HUMAN_VS_AI_INPUT:
                title_text = FONT.render(f"ENTER YOUR NAME ({ai_difficulty} Mode)", True, text_color)
                title_rect = title_text.get_rect(center=(SCREEN.get_width() // 2, 100))
                SCREEN.blit(title_text, title_rect)
                human_player_input.draw(SCREEN, input_bg, input_active, text_color)
                human_vs_ai_start_button.draw(SCREEN, button_color, hover_color, text_color)
                human_vs_ai_back_button.draw(SCREEN, button_color, hover_color, text_color)

            if has_images and sun_img and moon_img:
                mode_button.image = moon_img if is_dark_mode else sun_img
            else:
                mode_button.text = "☀️" if not is_dark_mode else "🌙"
            mode_button.draw(SCREEN, button_color, hover_color, text_color)

        pygame.display.flip()
        clock.tick(60)

main_menu()
