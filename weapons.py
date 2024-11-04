import pygame
import json
import math
import os
from sounds import sounds
import config

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

class Weapon:
    def __init__(self, name, damage, fire_rate, ammo_capacity, reload_time, image, sound):
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate
        self.ammo_capacity = ammo_capacity
        self.current_ammo = ammo_capacity
        self.reload_time = reload_time
        self.image = image
        self.sound = sound
        self.last_shot_time = 0

    def can_fire(self, current_time):
        return current_time - self.last_shot_time >= self.fire_rate

    def fire(self, current_time):
        if self.current_ammo > 0 and self.can_fire(current_time):
            self.current_ammo -= 1
            self.last_shot_time = current_time
            return True
        return False

    def reload(self):
        self.current_ammo = self.ammo_capacity

def shoot(game_state, target_x, target_y):
    current_time = pygame.time.get_ticks()
    weapon = game_state.current_weapon
    
    if weapon.can_fire(current_time):
        if weapon.fire(current_time):
            # Calculate bullet direction and velocity
            player_screen_x = game_state.player_pos[0] - game_state.camera_pos[0]
            player_screen_y = game_state.player_pos[1] - game_state.camera_pos[1]
            dx = target_x - player_screen_x
            dy = target_y - player_screen_y
            angle = math.atan2(dy, dx)
            velocity_x = math.cos(angle) * game_state.bullet_speed
            velocity_y = math.sin(angle) * game_state.bullet_speed
            
            # Spawn the bullet at the player's world position
            start_x = game_state.player_pos[0] + math.cos(angle) * (game_state.player_size // 2)
            start_y = game_state.player_pos[1] + math.sin(angle) * (game_state.player_size // 2)
            
            game_state.add_bullet(start_x, start_y, velocity_x, velocity_y, weapon.damage)
            sounds.play_sound(weapon.sound)
            game_state.player_has_shot = True
            weapon.last_shot_time = current_time
            return True
    return False

def update_bullets(game_state):
    for bullet in game_state.bullets[:]:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]
        
        # Remove bullets that are far outside the visible area
        if (bullet[0] < game_state.camera_pos[0] - config.WIDTH or
            bullet[0] > game_state.camera_pos[0] + config.WIDTH * 2 or
            bullet[1] < game_state.camera_pos[1] - config.HEIGHT or
            bullet[1] > game_state.camera_pos[1] + config.HEIGHT * 2):
            game_state.remove_bullet(bullet)

def update_npc_bullets(game_state):
    for bullet in game_state.npc_bullets[:]:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]
        
        # Remove bullets that are outside the level bounds
        if (bullet[0] < 0 or bullet[0] > config.LEVEL_WIDTH or
            bullet[1] < 0 or bullet[1] > config.LEVEL_HEIGHT):
            game_state.npc_bullets.remove(bullet)
            continue

        bullet_rect = pygame.Rect(bullet[0] - game_state.bullet_size // 2, 
                                  bullet[1] - game_state.bullet_size // 2,
                                  game_state.bullet_size, 
                                  game_state.bullet_size)
        
        # Check collision with player
        if game_state.player_rect.colliderect(bullet_rect):
            game_state.damage_player(bullet[4])
            sounds.play_sound("pain")
            game_state.npc_bullets.remove(bullet)

        # Check collision with NPCs
        for npc in game_state.npcs:
            if npc.rect.colliderect(bullet_rect):
                npc.hit()  # Enemy takes damage
                if npc.health > 0:
                    sounds.play_sound("pain")
                game_state.npc_bullets.remove(bullet)
                if npc.health <= 0:
                    game_state.remove_npc(npc)
                    sounds.play_sound("dead")
                break  # Stop checking other NPCs for this bullet

def load_weapons(filename):
    # Create absolute path for the JSON file
    json_path = os.path.join(PROJECT_ROOT, filename)
    
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Could not find weapons file at: {json_path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Project root directory: {PROJECT_ROOT}")
        return []
    
    weapons = []
    for weapon_data in data['weapons']:
        try:
            # Create absolute path for the weapon image
            image_path = os.path.join(PROJECT_ROOT, weapon_data['image'])
            image = pygame.image.load(image_path).convert_alpha()
        except pygame.error as e:
            print(f"Couldn't load image {weapon_data['image']}: {e}")
            print(f"Tried to load from: {image_path}")
            image = pygame.Surface((32, 32))
            image.fill((255, 0, 255))
        
        # Load the weapon sound
        sound_name = f"weapon_{weapon_data['name'].lower().replace(' ', '_')}"
        sound_path = os.path.join(PROJECT_ROOT, weapon_data['sound'])
        sounds.load_sound(sound_name, sound_path)
        
        weapon = Weapon(
            name=weapon_data['name'],
            damage=weapon_data['damage'],
            fire_rate=weapon_data['fire_rate'],
            ammo_capacity=weapon_data['ammo_capacity'],
            reload_time=weapon_data['reload_time'],
            image=image,
            sound=sound_name
        )
        weapons.append(weapon)
    
    return weapons

def draw_npc_bullets(screen, game_state):
    for bullet in game_state.npc_bullets:
        bullet_screen_pos = (
            int(bullet[0] - game_state.camera_pos[0]),
            int(bullet[1] - game_state.camera_pos[1])
        )
        pygame.draw.circle(screen, config.BULLET, bullet_screen_pos, game_state.bullet_size)