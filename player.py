import pygame
import config
import graphics

PLAYER_SVG = '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
  <path d="M20 5 L35 35 L20 25 L5 35 Z" fill="#4a9eff" stroke="#2d5a8c" stroke-width="2"/>
  <circle cx="20" cy="20" r="5" fill="#ff4a4a"/>
</svg>
'''

PLAYER_SIZE = 40
PLAYER_SPEED = 5

def draw_player_health_bar(game_state):
    bar_width = 200
    bar_height = 20
    x = 10
    y = 10
    fill = (game_state.player_health / game_state.player_max_health) * bar_width
    outline_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    
    if game_state.player_health > game_state.player_max_health * 0.6:
        color = config.GREEN
    elif game_state.player_health > game_state.player_max_health * 0.3:
        color = config.YELLOW
    else:
        color = config.RED
    
    pygame.draw.rect(graphics.screen, color, fill_rect)
    pygame.draw.rect(graphics.screen, config.WHITE, outline_rect, 2)
    graphics.draw_text(f"{game_state.player_health}/{game_state.player_max_health}", config.WHITE, x + bar_width // 2, y + bar_height // 2)

def move_player(game_state, dx, dy):
    new_x = game_state.player_pos[0] + dx
    new_y = game_state.player_pos[1] + dy

    # Check collision with level boundaries
    new_x = max(game_state.player_size // 2, min(new_x, config.LEVEL_WIDTH - game_state.player_size // 2))
    new_y = max(game_state.player_size // 2, min(new_y, config.LEVEL_HEIGHT - game_state.player_size // 2))

    # Create a new rect for the proposed player position
    new_player_rect = pygame.Rect(new_x - game_state.player_size // 2, 
                                  new_y - game_state.player_size // 2, 
                                  game_state.player_size, 
                                  game_state.player_size)
    
    # Check collision with enemies
    collision = False
    for enemy in game_state.enemies:
        enemy_rect = pygame.Rect(enemy.pos.x, enemy.pos.y, game_state.enemy_size, game_state.enemy_size)
        if new_player_rect.colliderect(enemy_rect):
            collision = True
            break

    if not collision:
        # If no collision, update the position
        game_state.player_pos[0] = new_x
        game_state.player_pos[1] = new_y
        
        # Update camera position to center on player
        game_state.camera_pos[0] = game_state.player_pos[0] - config.WIDTH // 2
        game_state.camera_pos[1] = game_state.player_pos[1] - config.HEIGHT // 2
        
        # Ensure camera doesn't go out of bounds
        game_state.camera_pos[0] = max(0, min(game_state.camera_pos[0], config.LEVEL_WIDTH - config.WIDTH))
        game_state.camera_pos[1] = max(0, min(game_state.camera_pos[1], config.LEVEL_HEIGHT - config.HEIGHT))
        
        game_state.update_player_rect()