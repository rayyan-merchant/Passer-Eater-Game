import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 1000, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PASSER EATER")
FONT_T = pygame.font.Font(r"C:\Users\Me\Desktop\passer eater game\assets\font\RubikMonoOne-Regular.ttf", 36)
FONT = pygame.font.Font(r"C:\Users\Me\Desktop\passer eater game\assets\font\RubikMonoOne-Regular.ttf", 32)
FONT2 = pygame.font.Font(r"C:\Users\Me\Desktop\passer eater game\assets\font\RubikMonoOne-Regular.ttf", 15)

# Light Mode Colors
LIGHT_BG_COLOR = (255, 255, 255)
LIGHT_TEXT_COLOR = (0, 0, 0)
LIGHT_BUTTON_COLOR = (255, 223, 186)
LIGHT_HOVER_COLOR = (255, 183, 77)

# Dark Mode Colors
DARK_BG_COLOR = (24, 26, 34)
DARK_TEXT_COLOR = (245, 245, 245)
DARK_BUTTON_COLOR = (72, 61, 139)
DARK_HOVER_COLOR = (123, 104, 238)

# Initial Mode is Dark
is_dark_mode = True

# Load sun and moon images (or use text symbols if images aren't available)
try:
    sun_img = pygame.image.load(r"C:\Users\Me\Desktop\passer eater game\sunn.png").convert_alpha()
    moon_img = pygame.image.load(r"C:\Users\Me\Desktop\passer eater game\moon.webp").convert_alpha()
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

# --- Button Callbacks ---
def start_game():
    print("Start Game Clicked!")

def human_vs_human():
    print("Human vs Human Clicked!")

def human_vs_ai():
    print("Human vs AI Clicked!")

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

# --- Main Menu ---
def main_menu():
    global is_dark_mode

    # Create mode toggle button with appropriate image
    mode_button_img = moon_img if is_dark_mode else sun_img if has_images else None
    mode_button = Button("☀️" if not is_dark_mode else "🌙", 930, 20, 50, 50, toggle_mode, mode_button_img)

    while True:
        bg_color = DARK_BG_COLOR if is_dark_mode else LIGHT_BG_COLOR
        text_color = DARK_TEXT_COLOR if is_dark_mode else LIGHT_TEXT_COLOR
        button_color = DARK_BUTTON_COLOR if is_dark_mode else LIGHT_BUTTON_COLOR
        hover_color = DARK_HOVER_COLOR if is_dark_mode else LIGHT_HOVER_COLOR
        
        SCREEN.fill(bg_color)
        
        # Render heading
        line1 = FONT_T.render("WELCOME TO", True, text_color)
        line2 = FONT_T.render("PASSER EATER, CHAMP!", True, text_color)

        rect1 = line1.get_rect(center=(SCREEN.get_width() // 2, 50))
        rect2 = line2.get_rect(center=(SCREEN.get_width() // 2, 100))

        SCREEN.blit(line1, rect1)
        SCREEN.blit(line2, rect2)

        # Draw all buttons with current mode colors
        for button in buttons:
            button.draw(SCREEN, button_color, hover_color, text_color)

        # Update mode button image and draw it
        if has_images:
            mode_button.image = moon_img if is_dark_mode else sun_img
        else:
            mode_button.text = "☀️" if not is_dark_mode else "🌙"
        mode_button.draw(SCREEN, button_color, hover_color, text_color)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()
            for button in buttons:
                button.check_click(event)
            mode_button.check_click(event)

        pygame.display.flip()

# Buttons for the main menu
buttons = [
    Button("Start Game", 200, 150, 600, 60, start_game),
    Button("Human vs Human", 200, 240, 600, 60, human_vs_human),
    Button("Human vs AI", 200, 330, 600, 60, human_vs_ai),
    Button("Instructions", 200, 420, 600, 60, show_instructions),
    Button("Exit", 200, 510, 600, 60, exit_game),
]

main_menu()