import pygame
import json
import math
from sounds import sounds
import config

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

def update_enemy_bullets(game_state):
    for bullet in game_state.enemy_bullets[:]:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]
        
        # Remove bullets that are outside the level bounds
        if (bullet[0] < 0 or bullet[0] > config.LEVEL_WIDTH or
            bullet[1] < 0 or bullet[1] > config.LEVEL_HEIGHT):
            game_state.enemy_bullets.remove(bullet)
            continue

        bullet_rect = pygame.Rect(bullet[0] - game_state.bullet_size // 2, 
                                  bullet[1] - game_state.bullet_size // 2,
                                  game_state.bullet_size, 
                                  game_state.bullet_size)
        
        # Check collision with player
        if game_state.player_rect.colliderect(bullet_rect):
            game_state.damage_player(bullet[4])
            sounds.play_sound("pain")
            game_state.enemy_bullets.remove(bullet)

        # Check collision with enemies
        for enemy in game_state.enemies:
            if enemy.rect.colliderect(bullet_rect):
                enemy.hit()  # Enemy takes damage
                if enemy.health > 0:
                    sounds.play_sound("pain")
                game_state.enemy_bullets.remove(bullet)
                if enemy.health <= 0:
                    game_state.remove_enemy(enemy)
                    sounds.play_sound("dead")
                break  # Stop checking other enemies for this bullet

def load_weapons(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    
    weapons = []
    for weapon_data in data['weapons']:
        try:
            image = pygame.image.load(weapon_data['image']).convert_alpha()
        except pygame.error as e:
            print(f"Couldn't load image {weapon_data['image']}: {e}")
            image = pygame.Surface((32, 32))
            image.fill((255, 0, 255))
        
        # Load the weapon sound
        sound_name = f"weapon_{weapon_data['name'].lower().replace(' ', '_')}"
        sounds.load_sound(sound_name, weapon_data['sound'])
        
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

def draw_enemy_bullets(screen, game_state):
    for bullet in game_state.enemy_bullets:
        bullet_screen_pos = (
            int(bullet[0] - game_state.camera_pos[0]),
            int(bullet[1] - game_state.camera_pos[1])
        )
        pygame.draw.circle(screen, config.BULLET, bullet_screen_pos, game_state.bullet_size)