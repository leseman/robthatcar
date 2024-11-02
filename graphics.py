import pygame
import io
import config
from sounds import sounds

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption("Top-Down Shooter")

def svg_to_pygame_surface(svg_string, width, height):
    svg_bytes = svg_string.encode('utf-8')
    surf = pygame.image.load(io.BytesIO(svg_bytes), 'SVG')
    return pygame.transform.scale(surf, (width, height))

def draw_text(text, color, x, y, custom_font=None):
    if custom_font is None:
        custom_font = font
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)

def update_camera(game_state):
    # Center the camera on the player
    game_state.camera_pos[0] = game_state.player_pos[0] - config.WIDTH // 2
    game_state.camera_pos[1] = game_state.player_pos[1] - config.HEIGHT // 2
    
    # Ensure camera doesn't go out of bounds
    game_state.camera_pos[0] = max(0, min(game_state.camera_pos[0], config.LEVEL_WIDTH - config.WIDTH))
    game_state.camera_pos[1] = max(0, min(game_state.camera_pos[1], config.LEVEL_HEIGHT - config.HEIGHT))

def draw_floating_scores(screen, game_state):
    for score in game_state.floating_scores:
        # Calculate screen position
        screen_pos = (
            int(score['pos'].x - game_state.camera_pos[0]),
            int(score['pos'].y - game_state.camera_pos[1])
        )
        draw_text(score['text'], config.YELLOW, screen_pos[0], screen_pos[1])

def draw_hud(game_state):
    # Health bar
    health_bar_width = 200
    health_bar_height = 20
    health_bar_x = 10
    health_bar_y = config.HEIGHT - 60
    health_fill = (game_state.player_health / game_state.player_max_health) * health_bar_width
    
    pygame.draw.rect(screen, config.RED, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, config.GREEN, (health_bar_x, health_bar_y, health_fill, health_bar_height))
    pygame.draw.rect(screen, config.WHITE, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
    
    # Armor bar
    armor_bar_width = 200
    armor_bar_height = 20
    armor_bar_x = 10
    armor_bar_y = config.HEIGHT - 30
    armor_fill = (game_state.player_armor / game_state.player_max_armor) * armor_bar_width
    
    pygame.draw.rect(screen, config.GRAY, (armor_bar_x, armor_bar_y, armor_bar_width, armor_bar_height))
    pygame.draw.rect(screen, config.BLUE, (armor_bar_x, armor_bar_y, armor_fill, armor_bar_height))
    pygame.draw.rect(screen, config.WHITE, (armor_bar_x, armor_bar_y, armor_bar_width, armor_bar_height), 2)
    
    # Health and Armor text
    health_text = small_font.render(f"Health: {int(game_state.player_health)}", True, config.WHITE)
    armor_text = small_font.render(f"Armor: {int(game_state.player_armor)}", True, config.WHITE)

    screen.blit(health_text, (health_bar_x + health_bar_width + 10, health_bar_y))
    screen.blit(armor_text, (armor_bar_x + armor_bar_width + 10, armor_bar_y))

def draw_ammo(game_state):
    weapon = game_state.current_weapon
    ammo_text = font.render(f"{weapon.name}: {weapon.current_ammo}/{weapon.ammo_capacity}", True, config.WHITE)
    ammo_rect = ammo_text.get_rect()
    ammo_rect.bottomright = (config.WIDTH - 10, config.HEIGHT - 10)
    weapon_rect = weapon.image.get_rect()
    weapon_rect.bottomright = (ammo_rect.left - 10, config.HEIGHT - 10)
    screen.blit(ammo_text, ammo_rect)
    screen.blit(weapon.image, weapon_rect)

def game_over(game_state):
    sounds.play_sound("dead")
    sounds.fade_out_music(3000)
    game_state.update_high_score()  # Update high score before ending the game
    screen.fill(config.BLACK)  # Clear the screen
    draw_text("Game Over!", config.RED, config.WIDTH // 2, config.HEIGHT // 2)
    draw_text(f"Final Score: {game_state.score}", config.WHITE, config.WIDTH // 2, config.HEIGHT // 2 + 40)
    draw_text(f"High Score: {game_state.high_score}", config.WHITE, config.WIDTH // 2, config.HEIGHT // 2 + 80)
    pygame.display.flip()
    pygame.time.wait(3000)