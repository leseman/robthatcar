import pygame
import sys
import json
import math
import graphics
import config
import inputs
from sounds import sounds

def main_menu():
    while True:
        high_score = inputs.load_high_score()
        graphics.screen.fill(config.BLACK)
        graphics.draw_text("Top-Down Shooter", config.WHITE, config.WIDTH // 2, config.HEIGHT // 4)
        graphics.draw_text(f"High Score: {high_score}", config.WHITE, config.WIDTH // 2, config.HEIGHT // 3)
        
        mx, my = pygame.mouse.get_pos()
        
        button_1 = pygame.Rect(config.WIDTH // 2 - 100, config.HEIGHT // 2, 200, 50)
        button_2 = pygame.Rect(config.WIDTH // 2 - 100, config.HEIGHT // 2 + 70, 200, 50)
        button_3 = pygame.Rect(config.WIDTH // 2 - 100, config.HEIGHT // 2 + 140, 200, 50)
        button_4 = pygame.Rect(config.WIDTH // 2 - 100, config.HEIGHT // 2 + 210, 200, 50)
        
        pygame.draw.rect(graphics.screen, config.WHITE, button_1)
        pygame.draw.rect(graphics.screen, config.WHITE, button_2)
        pygame.draw.rect(graphics.screen, config.WHITE, button_3)
        pygame.draw.rect(graphics.screen, config.WHITE, button_4)
        
        graphics.draw_text("Start Game", config.BLACK, config.WIDTH // 2, config.HEIGHT // 2 + 25)
        graphics.draw_text("Help", config.BLACK, config.WIDTH // 2, config.HEIGHT // 2 + 95)
        graphics.draw_text("Settings", config.BLACK, config.WIDTH // 2, config.HEIGHT // 2 + 165)
        graphics.draw_text("Exit", config.BLACK, config.WIDTH // 2, config.HEIGHT // 2 + 235)
        
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        
        if button_1.collidepoint((mx, my)):
            if click:
                return "start"
        if button_2.collidepoint((mx, my)):
            if click:
                return "help"
        if button_3.collidepoint((mx, my)):
            if click:
                return "settings"
        if button_4.collidepoint((mx, my)):
            if click:
                return "exit"
        
        pygame.display.update()

def help_menu():
    running = True
    while running:
        graphics.screen.fill(config.BLACK)
        graphics.draw_text("Help", config.WHITE, config.WIDTH // 2, config.HEIGHT // 4)
        graphics.draw_text("Use WASD keys to move", config.WHITE, config.WIDTH // 2, config.HEIGHT // 2 - 60)
        graphics.draw_text("Left-click to shoot", config.WHITE, config.WIDTH // 2, config.HEIGHT // 2 - 20)
        graphics.draw_text("Avoid enemies", config.WHITE, config.WIDTH // 2, config.HEIGHT // 2 + 20)
        graphics.draw_text("3 hits to kill an enemy", config.WHITE, config.WIDTH // 2, config.HEIGHT // 2 + 60)
        graphics.draw_text("Press ESC to return to main menu", config.WHITE, config.WIDTH // 2, config.HEIGHT * 3 // 4)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        pygame.display.update()

def settings_menu():
    controls = load_controls()
    music_volume, sfx_volume = load_volume_settings()
    
    running = True
    selected_control = None
    
    title_offset = config.HEIGHT // 12
    y_start = config.HEIGHT // 6
    button_height = min(40, config.HEIGHT // 15)
    button_width = min(300, config.WIDTH // 2)
    spacing = min(20, config.HEIGHT // 30)
    
    while running:
        graphics.screen.fill(config.BLACK)
        graphics.draw_text("Settings", config.WHITE, config.WIDTH // 2, title_offset, graphics.small_font)
        
        for i, (action, control) in enumerate(controls.items()):
            button = pygame.Rect(config.WIDTH // 2 - button_width // 2, 
                               y_start + i * (button_height + spacing), 
                               button_width, button_height)
            pygame.draw.rect(graphics.screen, config.WHITE, button, 2)
            if action == selected_control:
                graphics.draw_text(f"{action}: Click mouse or press key", config.RED, config.WIDTH // 2, 
                         y_start + i * (button_height + spacing) + button_height // 2, 
                         graphics.small_font)
            else:
                graphics.draw_text(f"{action}: {inputs.get_control_name(control)}", 
                         config.WHITE, config.WIDTH // 2, 
                         y_start + i * (button_height + spacing) + button_height // 2, 
                         graphics.small_font)
        
        volume_y = y_start + len(controls) * (button_height + spacing) + spacing
        graphics.draw_text(f"Music Volume: {int(music_volume * 100)}%", 
                 config.WHITE, config.WIDTH // 2, volume_y, graphics.small_font)
        
        music_rect = pygame.Rect(config.WIDTH // 4, volume_y + spacing, config.WIDTH // 2, button_height // 2)
        pygame.draw.rect(graphics.screen, config.WHITE, music_rect, 2)
        pygame.draw.rect(graphics.screen, config.WHITE, 
                        (config.WIDTH // 4, volume_y + spacing, 
                         int(config.WIDTH // 2 * music_volume), button_height // 2))
        
        graphics.draw_text(f"SFX Volume: {int(sfx_volume * 100)}%", 
                 config.WHITE, config.WIDTH // 2, volume_y + button_height + spacing, graphics.small_font)
        
        sfx_rect = pygame.Rect(config.WIDTH // 4, 
                              volume_y + button_height + spacing * 2, 
                              config.WIDTH // 2, button_height // 2)
        pygame.draw.rect(graphics.screen, config.WHITE, sfx_rect, 2)
        pygame.draw.rect(graphics.screen, config.WHITE, 
                        (config.WIDTH // 4, volume_y + button_height + spacing * 2, 
                         int(config.WIDTH // 2 * sfx_volume), button_height // 2))
        
        reset_button = pygame.Rect(config.WIDTH // 2 - button_width // 2, 
                                 volume_y + button_height * 2 + spacing * 3, 
                                 button_width, button_height)
        pygame.draw.rect(graphics.screen, config.WHITE, reset_button, 2)
        graphics.draw_text("Reset to Defaults", config.WHITE, config.WIDTH // 2, 
                 volume_y + button_height * 2 + spacing * 3 + button_height // 2, 
                 graphics.small_font)
    
        graphics.draw_text("Press ESC to save and return to main menu", config.WHITE, 
                 config.WIDTH // 2, config.HEIGHT - button_height, graphics.small_font)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_controls(controls)
                    save_volume_settings(music_volume, sfx_volume)
                    running = False
                elif selected_control:
                    controls[selected_control] = event.key
                    selected_control = None
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if selected_control:
                    controls[selected_control] = event.button
                    selected_control = None
                else:
                    for i, action in enumerate(controls):
                        button = pygame.Rect(config.WIDTH // 2 - button_width // 2, 
                                          y_start + i * (button_height + spacing), 
                                          button_width, button_height)
                        if button.collidepoint((mx, my)):
                            selected_control = action
                    if music_rect.collidepoint((mx, my)):
                        music_volume = (mx - config.WIDTH // 4) / (config.WIDTH // 2)
                        music_volume = max(0, min(1, music_volume))
                        sounds.set_music_volume(music_volume)
                    if sfx_rect.collidepoint((mx, my)):
                        sfx_volume = (mx - config.WIDTH // 4) / (config.WIDTH // 2)
                        sfx_volume = max(0, min(1, sfx_volume))
                        sounds.set_sfx_volume(sfx_volume)
                    if reset_button.collidepoint((mx, my)):
                        controls = inputs.DEFAULT_CONTROLS.copy()
                        music_volume = 0.5
                        sfx_volume = 0.5
                        sounds.set_music_volume(music_volume)
                        sounds.set_sfx_volume(sfx_volume)

def load_controls():
    try:
        with open("controls.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return inputs.DEFAULT_CONTROLS

def save_controls(controls):
    with open("controls.json", "w") as f:
        json.dump(controls, f)

def load_volume_settings():
    try:
        with open("volume_settings.json", "r") as f:
            settings = json.load(f)
            return settings["music"], settings["sfx"]
    except FileNotFoundError:
        return 0.5, 0.5  # Default to 50% volume

def save_volume_settings(music_volume, sfx_volume):
    with open("volume_settings.json", "w") as f:
        json.dump({"music": music_volume, "sfx": sfx_volume}, f)

def pause_menu(game_state):
    pause_menu_running = True
    while pause_menu_running:
        graphics.screen.fill((0, 0, 0, 128))  # Semi-transparent black
        graphics.draw_text("PAUSED", config.WHITE, config.WIDTH // 2, config.HEIGHT // 3)
        graphics.draw_text("Press ESC to resume", config.WHITE, config.WIDTH // 2, config.HEIGHT // 2)
        graphics.draw_text("Press M to return to main menu", config.WHITE, config.WIDTH // 2, config.HEIGHT // 2 + 40)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_menu_running = False
                elif event.key == pygame.K_m:
                    return "main_menu"
        
        pygame.display.flip()
    
    game_state.paused = False

class WeaponWheel:
    def __init__(self, weapons):
        self.weapons = weapons
        self.active = False
        self.selected = 0
        # Remove alpha channel for solid appearance
        self.wheel_surface = pygame.Surface((400, 400), pygame.SRCALPHA)
        self.center = (200, 200)
        self.radius = 150
        
        # Pre-scale weapon images for the wheel
        self.scaled_images = []
        for weapon in weapons:
            try:
                scaled_image = pygame.transform.scale(weapon.image, (48, 48))  # Slightly larger icons
                self.scaled_images.append(scaled_image)
            except Exception as e:
                print(f"Error scaling image for {weapon.name}: {e}")
                placeholder = pygame.Surface((48, 48))
                placeholder.fill((100, 100, 100))  # Gray placeholder instead of magenta
                self.scaled_images.append(placeholder)

    def draw(self, screen):
        if not self.active:
            return

        # Fill with dark background
        self.wheel_surface.fill((30, 30, 40))  # Dark blue-gray background

        segment_angle = 2 * math.pi / len(self.weapons)
        
        # Draw outer circle first
        pygame.draw.circle(self.wheel_surface, (50, 50, 60), self.center, self.radius + 20)
        
        # Draw segments and weapons
        for i, weapon in enumerate(self.weapons):
            start_angle = i * segment_angle - math.pi / 2
            end_angle = (i + 1) * segment_angle - math.pi / 2
            
            # Draw segment with gradient effect
            if i == self.selected:
                segment_color = (80, 120, 180)  # Highlighted blue
                border_color = (100, 160, 255)  # Bright blue border
            else:
                segment_color = (60, 60, 70)  # Dark gray
                border_color = (80, 80, 90)  # Slightly lighter border
            
            # Draw main segment
            pygame.draw.arc(self.wheel_surface, segment_color, 
                          (60, 60, 280, 280), start_angle, end_angle, 80)
            # Draw border
            pygame.draw.arc(self.wheel_surface, border_color,
                          (60, 60, 280, 280), start_angle, end_angle, 2)

            # Calculate positions
            mid_angle = (start_angle + end_angle) / 2
            
            # Draw weapon icon
            if i < len(self.scaled_images):
                image = self.scaled_images[i]
                icon_distance = self.radius * 0.65
                icon_x = self.center[0] + math.cos(mid_angle) * icon_distance
                icon_y = self.center[1] + math.sin(mid_angle) * icon_distance
                
                # Draw icon background circle
                pygame.draw.circle(self.wheel_surface, border_color, 
                                (int(icon_x), int(icon_y)), 30)
                
                image_rect = image.get_rect(center=(int(icon_x), int(icon_y)))
                self.wheel_surface.blit(image, image_rect)
            
            # Draw weapon name with better font and shadow
            font = pygame.font.Font(None, 28)  # Slightly larger font
            
            # Draw shadow first
            name_text_shadow = font.render(weapon.name, True, (0, 0, 0))
            text_distance = self.radius * 0.35
            text_x = self.center[0] + math.cos(mid_angle) * text_distance
            text_y = self.center[1] + math.sin(mid_angle) * text_distance
            text_rect_shadow = name_text_shadow.get_rect(center=(int(text_x + 2), int(text_y + 2)))
            self.wheel_surface.blit(name_text_shadow, text_rect_shadow)
            
            # Draw actual text
            name_text = font.render(weapon.name, True, (255, 255, 255))
            text_rect = name_text.get_rect(center=(int(text_x), int(text_y)))
            self.wheel_surface.blit(name_text, text_rect)
            
            # Draw weapon stats with improved styling
            stats_text = f"DMG: {weapon.damage}"
            stats_font = pygame.font.Font(None, 24)
            stats = stats_font.render(stats_text, True, (180, 180, 200))
            stats_distance = self.radius * 0.85
            stats_x = self.center[0] + math.cos(mid_angle) * stats_distance
            stats_y = self.center[1] + math.sin(mid_angle) * stats_distance
            stats_rect = stats.get_rect(center=(int(stats_x), int(stats_y)))
            self.wheel_surface.blit(stats, stats_rect)

        # Draw center hub
        hub_radius = 40
        pygame.draw.circle(self.wheel_surface, (50, 50, 60), self.center, hub_radius)  # Outer circle
        pygame.draw.circle(self.wheel_surface, (80, 80, 90), self.center, hub_radius - 2)  # Inner circle
        
        # Draw selection indicator
        if self.selected >= 0:
            arrow_angle = self.selected * segment_angle - math.pi / 2
            arrow_length = hub_radius - 5
            arrow_end_x = self.center[0] + math.cos(arrow_angle) * arrow_length
            arrow_end_y = self.center[1] + math.sin(arrow_angle) * arrow_length
            
            # Draw arrow with glow effect
            pygame.draw.line(self.wheel_surface, (100, 160, 255), 
                           self.center, (arrow_end_x, arrow_end_y), 4)
            pygame.draw.line(self.wheel_surface, (200, 220, 255), 
                           self.center, (arrow_end_x, arrow_end_y), 2)

        # Position the wheel on screen with a slight fade effect around edges
        screen_pos = (
            screen.get_width() // 2 - self.wheel_surface.get_width() // 2,
            screen.get_height() // 2 - self.wheel_surface.get_height() // 2
        )
        screen.blit(self.wheel_surface, screen_pos)

    def handle_mouse(self, mouse_pos):
        if not self.active:
            return

        # Get mouse position relative to wheel center
        wheel_x = self.wheel_surface.get_width() // 2
        wheel_y = self.wheel_surface.get_height() // 2
        
        screen_x = pygame.display.get_surface().get_width() // 2
        screen_y = pygame.display.get_surface().get_height() // 2
        
        dx = mouse_pos[0] - screen_x
        dy = mouse_pos[1] - screen_y
        
        # Calculate angle and adjust to start from top (-90 degrees)
        angle = math.atan2(dy, dx) + math.pi / 2
        if angle < 0:
            angle += 2 * math.pi

        # Determine selected weapon based on angle
        segment_angle = 2 * math.pi / len(self.weapons)
        self.selected = int(angle / segment_angle) % len(self.weapons)

    def get_selected_weapon(self):
        return self.weapons[self.selected]
    
    def toggle(self):
        self.active = not self.active