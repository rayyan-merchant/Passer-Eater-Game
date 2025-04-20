import pygame
import sys
from easy import easy_mode
from medium import medium_mode
from hard import hard_mode

pygame.init()

WIDTH, HEIGHT = 1000, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PASSER EATER")

FONT_T = pygame.font.Font("font/RubikMonoOne-Regular.ttf", 36)
FONT = pygame.font.Font("font/RubikMonoOne-Regular.ttf", 32)
FONT2 = pygame.font.Font("font/RubikMonoOne-Regular.ttf", 15)
INPUT_FONT = pygame.font.Font("font/RubikMonoOne-Regular.ttf", 24)

# Light Mode Colors
LIGHT_BG_COLOR = (255, 255, 255)
LIGHT_TEXT_COLOR = (0, 0, 0)
LIGHT_BUTTON_COLOR = (255, 223, 186)
LIGHT_HOVER_COLOR = (255, 183, 77)
LIGHT_INPUT_BG = (240, 240, 240)
LIGHT_INPUT_ACTIVE = (220, 220, 220)

# Dark Mode Colors
DARK_BG_COLOR = (24, 26, 34)
DARK_TEXT_COLOR = (245, 245, 245)
DARK_BUTTON_COLOR = (72, 61, 139)
DARK_HOVER_COLOR = (123, 104, 238)
DARK_INPUT_BG = (40, 42, 54)
DARK_INPUT_ACTIVE = (60, 62, 74)

# Initial Mode is Dark
is_dark_mode = True

# Menu states
MENU_MAIN = 0
MENU_GAME_TYPE = 1
MENU_HUMAN_VS_HUMAN_INPUT = 2
MENU_HUMAN_VS_AI_INPUT = 3
MENU_AI_DIFFICULTY = 4  # New menu state for difficulty selection
current_menu = MENU_MAIN

# Player names
player1_name = ""
player2_name = ""
ai_player_name = "AI"
human_player_name = ""
active_input = None

# AI difficulty
ai_difficulty = None  # Can be "Easy", "Medium", or "Hard"

# Load sun and moon images (or use text symbols if images aren't available)
try:
    sun_img = pygame.image.load(r"sunn.png").convert_alpha()
    moon_img = pygame.image.load(r"moon.webp").convert_alpha()
    sun_img = pygame.transform.scale(sun_img, (30, 30))
    moon_img = pygame.transform.scale(moon_img, (30, 30))
    has_images = True
except:
    has_images = False
    print("Image files not found, using text symbols instead")


# --- Button Class ---
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


# --- Input Box Class ---
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
                # Only add characters if the length is less than 15
                if len(self.text) < 15 and event.unicode.isalnum() or event.unicode == " ":
                    self.text += event.unicode
        return False

    def draw(self, surface, bg_color, active_color, text_color):
        # Draw the label
        label_surface = FONT2.render(self.label, True, text_color)
        surface.blit(label_surface, (self.rect.x, self.rect.y - 30))

        # Draw the input box
        pygame.draw.rect(surface, active_color if self.active else bg_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, text_color, self.rect, 2, border_radius=10)  # Border

        # Draw the text
        text_surface = INPUT_FONT.render(self.text, True, text_color)
        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))

        # Draw cursor if active
        if self.active and pygame.time.get_ticks() % 1000 < 500:
            text_width = INPUT_FONT.size(self.text)[0]
            cursor_pos = self.rect.x + 10 + text_width
            pygame.draw.line(surface, text_color, (cursor_pos, self.rect.y + 10),
                             (cursor_pos, self.rect.y + self.rect.height - 10), 2)


# --- Button Callbacks ---
def show_game_selection():
    global current_menu
    current_menu = MENU_GAME_TYPE


def back_to_main():
    global current_menu
    current_menu = MENU_MAIN


def back_to_game_selection():
    global current_menu
    current_menu = MENU_GAME_TYPE


def show_human_vs_human_input():
    global current_menu, player1_name, player2_name, active_input
    current_menu = MENU_HUMAN_VS_HUMAN_INPUT
    player1_name = ""
    player2_name = ""
    active_input = None


def show_ai_difficulty_selection():
    global current_menu
    current_menu = MENU_AI_DIFFICULTY


def set_difficulty(difficulty):
    global ai_difficulty, current_menu
    ai_difficulty = difficulty
    show_human_vs_ai_input()


def show_human_vs_ai_input():
    global current_menu, human_player_name, active_input
    current_menu = MENU_HUMAN_VS_AI_INPUT
    human_player_name = ""
    active_input = None


def start_human_vs_human_game():
    if player1_name.strip() and player2_name.strip():
        print(f"Starting Human vs Human game with players: {player1_name} and {player2_name}")
        # Game logic would start here
    else:
        print("Please enter names for both players")


def start_human_vs_ai_game():
    if human_player_name.strip():
        print(f"Starting Human vs AI game with player: {human_player_name} against AI on {ai_difficulty} difficulty")
        # Load appropriate AI module based on difficulty
        if ai_difficulty == "Easy":
            print("Loading easy_ai.py module")
            # Import and use easy_ai module here
        elif ai_difficulty == "Medium":
            print("Loading medium_ai.py module")
            # Import and use medium_ai module here
        elif ai_difficulty == "Hard":
            print("Loading hard_ai.py module")
            # Import and use hard_ai module here
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

        # Instruction text lines
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

        # Draw each line
        y = 25
        for line in instructions:
            text_surface = FONT2.render(line, True, text_color)
            SCREEN.blit(text_surface, (30, y))
            y += 20  # space between lines

        # Draw the Back button with dynamic colors
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
                    running = False  # return to main menu


def exit_game():
    pygame.quit()
    sys.exit()


def toggle_mode():
    global is_dark_mode
    is_dark_mode = not is_dark_mode


# --- Main Menu Buttons ---
main_menu_buttons = [
    Button("New Game", 200, 200, 600, 80, show_game_selection),
    Button("Instructions", 200, 320, 600, 80, show_instructions),
    Button("Quit Game", 200, 440, 600, 80, exit_game),
]

# --- Game Type Selection Buttons ---
game_type_buttons = [
    Button("Player vs Player", 200, 200, 600, 80, show_human_vs_human_input),
    Button("Player vs Computer", 200, 320, 600, 80, show_ai_difficulty_selection),
    Button("Back", 200, 440, 600, 80, back_to_main),
]

# --- Difficulty Selection Buttons ---
difficulty_buttons = [
    Button("Easy", 200, 160, 600, 80, lambda: set_difficulty("Easy")),
    Button("Medium", 200, 260, 600, 80, lambda: set_difficulty("Medium")),
    Button("Hard", 200, 360, 600, 80, lambda: set_difficulty("Hard")),
    Button("Back", 200, 460, 600, 80, back_to_game_selection),
]

# --- Input boxes for Human vs Human ---
player1_input = InputBox(250, 200, 500, 50, "Enter Player 1 (Passer) Name:")
player2_input = InputBox(250, 300, 500, 50, "Enter Player 2 (Eater) Name:")
human_vs_human_start_button = Button("Start Game", 350, 400, 300, 60, start_human_vs_human_game)
human_vs_human_back_button = Button("Back", 350, 480, 300, 60, show_game_selection)

# --- Input box for Human vs AI ---
human_player_input = InputBox(250, 250, 500, 50, "Enter Your Name:")
human_vs_ai_start_button = Button("Start Game", 350, 350, 300, 60, start_human_vs_ai_game)
human_vs_ai_back_button = Button("Back", 350, 430, 300, 60, show_ai_difficulty_selection)


# --- Main Game Loop ---
def main_menu():
    global is_dark_mode, current_menu, player1_name, player2_name, human_player_name, active_input

    # Create mode toggle button with appropriate image
    mode_button_img = moon_img if is_dark_mode else sun_img if has_images else None
    mode_button = Button("☀️" if not is_dark_mode else "🌙", 930, 20, 50, 50, toggle_mode, mode_button_img)

    clock = pygame.time.Clock()

    while True:
        # Set colors based on current mode
        bg_color = DARK_BG_COLOR if is_dark_mode else LIGHT_BG_COLOR
        text_color = DARK_TEXT_COLOR if is_dark_mode else LIGHT_TEXT_COLOR
        button_color = DARK_BUTTON_COLOR if is_dark_mode else LIGHT_BUTTON_COLOR
        hover_color = DARK_HOVER_COLOR if is_dark_mode else LIGHT_HOVER_COLOR
        input_bg = DARK_INPUT_BG if is_dark_mode else LIGHT_INPUT_BG
        input_active = DARK_INPUT_ACTIVE if is_dark_mode else LIGHT_INPUT_ACTIVE

        SCREEN.fill(bg_color)

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()

            # Handle mode toggle button in all menus
            mode_button.check_click(event)

            # Main menu buttons
            if current_menu == MENU_MAIN:
                for button in main_menu_buttons:
                    button.check_click(event)

            # Game type selection buttons
            elif current_menu == MENU_GAME_TYPE:
                for button in game_type_buttons:
                    button.check_click(event)

            # AI difficulty selection
            elif current_menu == MENU_AI_DIFFICULTY:
                for button in difficulty_buttons:
                    button.check_click(event)

            # Human vs Human input handling
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

            # Human vs AI input handling
            elif current_menu == MENU_HUMAN_VS_AI_INPUT:
                if human_player_input.handle_event(event):
                    human_player_name = human_player_input.text
                    active_input = None

                human_vs_ai_start_button.check_click(event)
                human_vs_ai_back_button.check_click(event)

        # Draw UI elements based on current menu
        if current_menu == MENU_MAIN:
            # Draw welcome message in main menu only
            line1 = FONT_T.render("WELCOME TO", True, text_color)
            line2 = FONT_T.render("PASSER EATER, CHAMP!", True, text_color)
            rect1 = line1.get_rect(center=(SCREEN.get_width() // 2, 50))
            rect2 = line2.get_rect(center=(SCREEN.get_width() // 2, 100))
            SCREEN.blit(line1, rect1)
            SCREEN.blit(line2, rect2)

            # Draw main menu buttons
            for button in main_menu_buttons:
                button.draw(SCREEN, button_color, hover_color, text_color)

        elif current_menu == MENU_GAME_TYPE:
            # Draw select game mode title
            select_text = FONT.render("SELECT GAME MODE", True, text_color)
            select_rect = select_text.get_rect(center=(SCREEN.get_width() // 2, 100))
            SCREEN.blit(select_text, select_rect)

            # Draw game type buttons
            for button in game_type_buttons:
                button.draw(SCREEN, button_color, hover_color, text_color)

        elif current_menu == MENU_AI_DIFFICULTY:
            # Draw select difficulty title
            diff_text = FONT.render("SELECT DIFFICULTY", True, text_color)
            diff_rect = diff_text.get_rect(center=(SCREEN.get_width() // 2, 100))
            SCREEN.blit(diff_text, diff_rect)

            # Draw difficulty buttons
            for button in difficulty_buttons:
                button.draw(SCREEN, button_color, hover_color, text_color)

        elif current_menu == MENU_HUMAN_VS_HUMAN_INPUT:
            # Draw title
            title_text = FONT.render("ENTER PLAYER NAMES", True, text_color)
            title_rect = title_text.get_rect(center=(SCREEN.get_width() // 2, 100))
            SCREEN.blit(title_text, title_rect)

            # Draw input boxes
            player1_input.draw(SCREEN, input_bg, input_active, text_color)
            player2_input.draw(SCREEN, input_bg, input_active, text_color)

            # Draw buttons
            human_vs_human_start_button.draw(SCREEN, button_color, hover_color, text_color)
            human_vs_human_back_button.draw(SCREEN, button_color, hover_color, text_color)

        elif current_menu == MENU_HUMAN_VS_AI_INPUT:
            # Draw title with difficulty info
            title_text = FONT.render(f"ENTER YOUR NAME ({ai_difficulty} Mode)", True, text_color)
            title_rect = title_text.get_rect(center=(SCREEN.get_width() // 2, 100))
            SCREEN.blit(title_text, title_rect)

            # Draw input box
            human_player_input.draw(SCREEN, input_bg, input_active, text_color)

            # Draw buttons
            human_vs_ai_start_button.draw(SCREEN, button_color, hover_color, text_color)
            human_vs_ai_back_button.draw(SCREEN, button_color, hover_color, text_color)

        # The mode button is always visible
        if has_images:
            mode_button.image = moon_img if is_dark_mode else sun_img
        else:
            mode_button.text = "☀️" if not is_dark_mode else "🌙"
        mode_button.draw(SCREEN, button_color, hover_color, text_color)

        pygame.display.flip()
        clock.tick(60)  # Cap at 60 FPS


# Start the game
main_menu()
