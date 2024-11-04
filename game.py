import pygame
pygame.init()
import sys
import os
import math
import config
import npc as npc
from npc import update_npcs, spawn_npc
import inputs
import logic
import graphics
import menu
import player
import weapons
import maps
from maps import Minimap
from pygame.math import Vector2
from collections import defaultdict
from sounds import sounds
from os import path

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

loaded_images = {}

for image_name, file_path in config.image_files.items():
    try:
        # Create absolute path for the image file
        abs_path = os.path.join(PROJECT_ROOT, file_path)
        loaded_images[image_name] = pygame.image.load(abs_path).convert_alpha()
    except (pygame.error, FileNotFoundError) as e:
        print(f"Couldn't load image {file_path}: {e}")
        print(f"Tried to load from: {abs_path}")
        loaded_images[image_name] = None

class GameState:
    def __init__(self):
        self.paused = False
        self.bullets = []
        self.npcs = []
        self.weapons = []
        self.floating_scores = []
        self.score = config.START_SCORE
        self.base_score = config.BASE_SCORE
        self.max_multiplier = config.MAX_MULTIPLIER
        self.high_score = inputs.load_high_score()
        self.player_max_health = config.PLAYER_MAX_HEALTH
        self.player_health = self.player_max_health
        self.player_max_armor = config.PLAYER_MAX_ARMOR
        self.player_armor = self.player_max_armor
        self.armor_effectiveness = config.ARMOR_EFFECTIVENESS
        self.width = config.WIDTH
        self.height = config.HEIGHT
        self.player_pos = [config.LEVEL_WIDTH // 2, config.LEVEL_HEIGHT // 2]  # Start at center of level
        self.camera_pos = [self.player_pos[0] - config.WIDTH // 2, self.player_pos[1] - config.HEIGHT // 2]
        self.player_size = player.PLAYER_SIZE
        self.player_speed = player.PLAYER_SPEED
        self.npc_size = npc.NPC_SIZE
        self.npc_speed = npc.NPC_SPEED
        self.npc_spawn_rate = npc.NPC_SPAWN_RATE
        self.player_surface = self.create_player_surface()
        self.player_collision_cooldown = 0
        self.tilemap = maps.TileMap(config.LEVEL_WIDTH // config.TILE_SIZE, config.LEVEL_HEIGHT // config.TILE_SIZE)
        self.tilemap.generate_wfc_map()
        self.player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], self.player_size, self.player_size)
        self.bullet_speed = 10
        self.bullet_size = 5
        self.npc_bullets = []
        self.shoot_cooldown = 0
        self.weapons = weapons.load_weapons('weapons.json')
        self.player_has_shot = False
        self._current_weapon = None
        self.current_weapon_index = 0
        self.pistol = self.get_pistol() 
        if not self.weapons:
            print("No weapons loaded. Check your weapons.json file.")
            pygame.quit()
            sys.exit()

        self.minimap = Minimap(
            config.WIDTH,
            config.HEIGHT,
            config.LEVEL_WIDTH,
            config.LEVEL_HEIGHT
        )

    @property
    def current_weapon(self):
        if self._current_weapon is None and self.weapons:
            self._current_weapon = self.weapons[0]
        return self._current_weapon
    
    @current_weapon.setter
    def current_weapon(self, weapon):
        self._current_weapon = weapon
    
    def switch_weapon(self):
        self.current_weapon_index = (self.current_weapon_index + 1) % len(self.weapons)
        self._current_weapon = self.weapons[self.current_weapon_index]
        sounds.play_sound('switch')

    def get_pistol(self):
        for weapon in self.weapons:
            if weapon.name.lower() == "pistol":
                return weapon
        # If no pistol is found, return the first weapon (or None if no weapons)
        return self.weapons[0] if self.weapons else None
        
    def create_player_surface(self):
        return graphics.svg_to_pygame_surface(player.PLAYER_SVG, self.player_size, self.player_size)
    
    def update_player_rect(self):
        self.player_rect.x = self.player_pos[0] - self.player_size // 2
        self.player_rect.y = self.player_pos[1] - self.player_size // 2

    def add_bullet(self, x, y, vx, vy, damage):
        self.bullets.append([x, y, vx, vy, damage])

    def remove_bullet(self, bullet):
        self.bullets.remove(bullet)

    def add_npc(self, npc):
        self.npcs.append(npc)

    def remove_npc(self, npc):
        self.npcs.remove(npc)

    def add_npc_bullet(self, x, y, vx, vy, damage):
        self.npc_bullets.append([x, y, vx, vy, damage])

    def damage_player(self, damage):
        if self.player_armor > 0:
            armor_absorption = min(damage * self.armor_effectiveness, self.player_armor)
            self.player_armor -= armor_absorption
            remaining_damage = damage - armor_absorption
            self.player_health -= remaining_damage
        else:
            self.player_health -= damage

        # Ensure health and armor don't go below 0
        self.player_health = max(0, self.player_health)
        self.player_armor = max(0, self.player_armor)
    
    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            inputs.save_high_score(self.high_score)

    def add_floating_score(self, score, pos):
        self.floating_scores.append({
            'text': str(score),
            'pos': Vector2(pos),
            'time': 60
        })

def main():
    while True:
        choice = menu.main_menu()
        if choice == "start":
            result = game()
            if result == "main_menu":
                continue
        elif choice == "help":
            menu.help_menu()
        elif choice == "settings":
            menu.settings_menu()
        elif choice == "exit":
            break

def game():
    game_state = GameState()
    controls = menu.load_controls()
    music_volume, sfx_volume = menu.load_volume_settings()
    sounds.set_music_volume(music_volume)
    sounds.set_sfx_volume(sfx_volume)
    sounds.play_music()
    weapon_wheel = menu.WeaponWheel(game_state.weapons)
    
    running = True
    clock = pygame.time.Clock()
    spawn_timer = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == controls["switch_weapon"]:
                    game_state.switch_weapon()
                if event.key == controls["weapon_wheel"]:
                    weapon_wheel.active = True
                    pygame.mouse.set_visible(True)
                if event.key == pygame.K_ESCAPE:
                    if game_state.paused:
                        game_state.paused = False
                    else:
                        result = menu.pause_menu(game_state)
                        if result == "main_menu":
                            return "main_menu"
                elif event.key == pygame.K_m:
                    return "main_menu"
            if event.type == pygame.KEYUP:
                if event.key == controls["weapon_wheel"]:
                    weapon_wheel.active = False
                    game_state.current_weapon = weapon_wheel.get_selected_weapon()
            if not game_state.paused:
                if event.type == pygame.MOUSEBUTTONDOWN and 1 <= controls["shoot"] <= 5:
                    if event.button == controls["shoot"]:
                        mx, my = pygame.mouse.get_pos()
                        weapons.shoot(game_state, mx, my)
                elif event.type == pygame.KEYDOWN:
                    if event.key == controls["shoot"]:
                        mx, my = pygame.mouse.get_pos()
                        weapons.shoot(game_state, mx, my)

        # Handle player movement
        if not game_state.paused:
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[controls["left"]]:
                dx -= game_state.player_speed
            if keys[controls["right"]]:
                dx += game_state.player_speed
            if keys[controls["up"]]:
                dy -= game_state.player_speed
            if keys[controls["down"]]:
                dy += game_state.player_speed
        
            player.move_player(game_state, dx, dy)
            graphics.update_camera(game_state)

            # Update game state
            weapons.update_bullets(game_state)
            weapons.update_npc_bullets(game_state)
            update_npcs(game_state)
            logic.update_floating_scores(game_state)
            game_state.update_player_rect()

            if weapon_wheel.active:
                weapon_wheel.handle_mouse(pygame.mouse.get_pos())
        
            spawn_timer += 1
            if spawn_timer >= game_state.npc_spawn_rate:
                spawn_npc(game_state)
                spawn_timer = 0
        
            if game_state.player_collision_cooldown > 0:
                game_state.player_collision_cooldown -= 1
            
            if game_state.shoot_cooldown > 0:
                game_state.shoot_cooldown -= 1
            
            # Check for player collision after all updates
            if game_state.player_health <= 0:
                running = False
                graphics.game_over(game_state)
                break  # Exit the game loop immediately
        
        # Drawing code
        graphics.screen.fill(config.BLACK)
        maps.render_tilemap(graphics.screen, game_state.tilemap, game_state.camera_pos)
        weapon_wheel.draw(graphics.screen)
        game_state.minimap.update(game_state)
        game_state.minimap.draw(graphics.screen)
        
        # Draw player
        player_screen_pos = (
            game_state.player_pos[0] - game_state.camera_pos[0],
            game_state.player_pos[1] - game_state.camera_pos[1]
        )
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = math.atan2(mouse_y - player_screen_pos[1], 
                           mouse_x - player_screen_pos[0])
        rotated_player = pygame.transform.rotate(game_state.player_surface, 
                                                 math.degrees(-angle) - 90)
        player_rect = rotated_player.get_rect(center=player_screen_pos)
        graphics.screen.blit(rotated_player, player_rect)
        
        # Draw NPCs
        for npc in game_state.npcs:
            npc.draw(graphics.screen, game_state.camera_pos)
        
        # Draw bullets
        for bullet in game_state.bullets:
            bullet_screen_pos = (
                int(bullet[0] - game_state.camera_pos[0]),
                int(bullet[1] - game_state.camera_pos[1])
            )
            pygame.draw.circle(graphics.screen, config.BULLET, bullet_screen_pos, game_state.bullet_size)

        
        for bullet in game_state.npc_bullets:
            bullet_screen_pos = (
                int(bullet[0] - game_state.camera_pos[0]),
                int(bullet[1] - game_state.camera_pos[1])
            )
            pygame.draw.circle(graphics.screen, config.BULLET, bullet_screen_pos, game_state.bullet_size)

        # Display score, HUD
        graphics.draw_text(f"$ {game_state.score}", config.WHITE, config.WIDTH - 100, 30)
        graphics.draw_hud(game_state)
        graphics.draw_ammo(game_state)
        graphics.draw_floating_scores(graphics.screen, game_state)

        if game_state.paused:
            graphics.draw_text("PAUSED", config.WHITE, config.WIDTH // 2, config.HEIGHT // 2)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()