import pygame
from pygame.math import Vector2
import random
import math
import config
from sounds import sounds
import logic

ENEMY_SIZE = 30
ENEMY_SPEED = 2
ENEMY_HEALTH = 5
ENEMY_SPAWN_RATE = 60
ENEMY_BULLET_SPEED = 5
ALERT_RADIUS = 200

class Enemy:
    def __init__(self, x, y, game_state):
        self.pos = Vector2(x, y)
        self.max_health = ENEMY_HEALTH
        self.health = self.max_health
        self.bullet_speed = ENEMY_BULLET_SPEED
        self.state = "walk"
        self.direction = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.rect = pygame.Rect(x, y, game_state.enemy_size, game_state.enemy_size)
        self.collision_cooldown = 0
        self.state_timer = random.randint(60, 180)
        self.has_gun = random.random() < 0.1  # 10% chance to have a gun
        self.shoot_cooldown = 0
        self.is_alerted = False
        self.alert_cooldown = 0  # Add cooldown for alert state
        self.game_state = game_state
        self.weapon = game_state.get_pistol() if self.has_gun else None
        self.reaction_time = random.randint(30, 90) 

        if self.weapon:
            self.actual_fire_rate = int(self.weapon.fire_rate * random.uniform(0.9, 1.1))
        else:
            self.actual_fire_rate = 0

    def update(self):
        self.move()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.alert_cooldown > 0:
            self.alert_cooldown -= 1
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        
        # Only shoot if alerted and after reaction time has passed
        if self.is_alerted and self.has_gun and self.alert_cooldown <= 0:
            self.shoot()

    def shoot(self):
        if self.weapon and self.shoot_cooldown <= 0:
            # Calculate distance to player
            distance = (Vector2(self.game_state.player_pos) - self.pos).length()
            
            # Only shoot if player is within range (adjust range as needed)
            if distance < 300:  # Maximum shooting range
                direction = (Vector2(self.game_state.player_pos) - self.pos).normalize()
                bullet_pos = self.pos + direction * self.game_state.enemy_size
                
                # Add some inaccuracy based on distance
                accuracy = 1 - (distance / 600)  # More accurate at closer range
                angle_variation = random.uniform(-20 * (1 - accuracy), 20 * (1 - accuracy))
                direction = direction.rotate(angle_variation)
                
                self.game_state.add_enemy_bullet(
                    bullet_pos.x, bullet_pos.y, 
                    direction.x * self.bullet_speed, 
                    direction.y * self.bullet_speed, 
                    self.weapon.damage
                )
                sounds.play_sound(self.weapon.sound)
                self.shoot_cooldown = self.weapon.fire_rate
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.game_state.remove_enemy(self)
        
        # Set alert state with reaction time delay
        if not self.is_alerted:
            self.is_alerted = True
            self.alert_cooldown = self.reaction_time
            self.alert_nearby_enemies()

    def alert_nearby_enemies(self):
        for enemy in self.game_state.enemies:
            if enemy != self and enemy.has_gun and not enemy.is_alerted:
                distance = self.pos.distance_to(enemy.pos)
                if distance < ALERT_RADIUS:
                    enemy.is_alerted = True
                    enemy.alert_cooldown = enemy.reaction_time  # Give each enemy their own reaction time

    def move(self):
        if self.state == "walk":
            self.pos += self.direction * self.game_state.enemy_speed
        elif self.state == "idle":
            pass  # Do nothing when idle

        # Keep enemy within screen bounds
        self.pos.x = max(0, min(self.pos.x, config.LEVEL_WIDTH - self.game_state.enemy_size))
        self.pos.y = max(0, min(self.pos.y, config.LEVEL_HEIGHT - self.game_state.enemy_size))

        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Update state timer and change state if needed
        self.state_timer -= 1
        if self.state_timer <= 0:
            self.change_state()

    def change_state(self):
        if self.state == "walk":
            if random.random() < 0.3:  # 30% chance to stop
                self.state = "idle"
                self.state_timer = random.randint(30, 90)  # Idle for 0.5-1.5 seconds
            else:
                # Change direction
                self.direction = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
                self.state_timer = random.randint(60, 180)  # Walk for 1-3 seconds
        else:  # If idle, start walking again
            self.state = "walk"
            self.direction = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
            self.state_timer = random.randint(60, 180)  # Walk for 1-3 seconds

    def draw(self, screen, camera_pos):
        screen_pos = (
            self.pos.x - camera_pos[0],
            self.pos.y - camera_pos[1]
        )
        # Render if the enemy is within or near the viewport
        if (-self.game_state.enemy_size <= screen_pos[0] < config.WIDTH + self.game_state.enemy_size and
            -self.game_state.enemy_size <= screen_pos[1] < config.HEIGHT + self.game_state.enemy_size):
            pygame.draw.rect(screen, config.RED, 
                             (screen_pos[0], screen_pos[1], 
                              self.game_state.enemy_size, self.game_state.enemy_size))
            if self.has_gun:
                gun_size = 10
                pygame.draw.rect(screen, config.YELLOW, 
                                 (screen_pos[0] + self.game_state.enemy_size - gun_size, 
                                  screen_pos[1], gun_size, gun_size))
            self.draw_health_bar(screen, camera_pos)

    def draw_health_bar(self, screen, camera_pos):
        bar_width = self.game_state.enemy_size
        bar_height = 5
        fill = (self.health / self.max_health) * bar_width
        screen_pos = (self.pos.x - camera_pos[0], self.pos.y - camera_pos[1])
        
        # Render if the enemy is within or near the viewport
        if (-self.game_state.enemy_size <= screen_pos[0] < config.WIDTH + self.game_state.enemy_size and
            -self.game_state.enemy_size <= screen_pos[1] < config.HEIGHT + self.game_state.enemy_size):
            outline_rect = pygame.Rect(int(screen_pos[0]), int(screen_pos[1]) - 10, bar_width, bar_height)
            fill_rect = pygame.Rect(int(screen_pos[0]), int(screen_pos[1]) - 10, fill, bar_height)

            if self.health > self.max_health * 0.6:
                color = config.GREEN
            elif self.health > self.max_health * 0.3:
                color = config.YELLOW
            else:
                color = config.RED

            pygame.draw.rect(screen, color, fill_rect)
            pygame.draw.rect(screen, config.WHITE, outline_rect, 1)

    def hit(self, damage=1):    
        if random.random() < 0.1:  # 10% chance of critical hit
            self.health = max(0, self.health - 2)  # Critical hit does extra damage
        else:
            self.health = max(0, self.health - damage)
        
        if self.health > 0:
            sounds.play_sound("pain")
            rand = random.random()
            if rand < 0.1:
                self.behavior = "shoot"
            elif rand < 0.8:
                self.behavior = "flee"
                self.direction = (Vector2(self.game_state.player_pos) - self.pos).normalize() * -1
            else:
                self.behavior = "walk"

def update_enemies(game_state):
    for enemy in game_state.enemies[:]:
        enemy.update()

        screen_pos = (enemy.pos.x - game_state.camera_pos[0], 
                      enemy.pos.y - game_state.camera_pos[1])
        if (screen_pos[0] < -config.WIDTH or screen_pos[0] > config.WIDTH*2 or 
            screen_pos[1] < -config.HEIGHT or screen_pos[1] > config.HEIGHT*2):
            game_state.remove_enemy(enemy)
            continue

        # Allow enemies with guns to shoot periodically
        if enemy.has_gun and enemy.shoot_cooldown <= 0:
            enemy.shoot()

        # Check for collisions with player
        player_rect = pygame.Rect(game_state.player_pos[0] - game_state.player_size // 2,
                                  game_state.player_pos[1] - game_state.player_size // 2,
                                  game_state.player_size, game_state.player_size)
        enemy_rect = pygame.Rect(enemy.pos.x, enemy.pos.y, game_state.enemy_size, game_state.enemy_size)
        
        if player_rect.colliderect(enemy_rect):
            # Move enemy away from player
            direction = enemy.pos - Vector2(game_state.player_pos)
            if direction.length() > 0:
                direction = direction.normalize()
                enemy.pos += direction * game_state.enemy_speed
        
        # Check for collisions with bullets
        for bullet in game_state.bullets[:]:
            if (enemy.pos.x < bullet[0] < enemy.pos.x + game_state.enemy_size and
                enemy.pos.y < bullet[1] < enemy.pos.y + game_state.enemy_size):
                enemy.hit(bullet[4])
                game_state.remove_bullet(bullet)
                if enemy.health <= 0:
                    # Calculate distance between player and enemy
                    dx = enemy.pos.x - game_state.player_pos[0]
                    dy = enemy.pos.y - game_state.player_pos[1]
                    distance = math.sqrt(dx**2 + dy**2)
                    score = logic.calculate_score(distance, game_state)
                    game_state.score += score
                    sounds.play_sound("dead")
                    game_state.add_floating_score(score, enemy.pos)
                    game_state.remove_enemy(enemy)
                break

        # Check for collisions with other enemies
        for other in game_state.enemies:
            if enemy != other and enemy.collision_cooldown == 0 and other.collision_cooldown == 0:
                distance = enemy.pos.distance_to(other.pos)
                if distance < game_state.enemy_size:
                    # Collision detected, change directions
                    if distance > 0:
                        enemy.direction = (enemy.pos - other.pos).normalize()
                        other.direction = -enemy.direction
                    else:
                        # If distance is 0, give them random opposite directions
                        angle = random.uniform(0, 2 * math.pi)
                        enemy.direction = Vector2(math.cos(angle), math.sin(angle))
                        other.direction = -enemy.direction
                    
                    # Move enemies apart slightly to prevent sticking
                    separation = (enemy.direction * (game_state.enemy_size - distance + 1)) / 2
                    enemy.pos += separation
                    other.pos -= separation
                    
                    # Immediately change state after collision
                    enemy.change_state()
                    other.change_state()

def spawn_enemy(game_state):
    if len(game_state.enemies) < config.MAX_ENEMIES:
        margin = 200  # Distance outside viewport to spawn enemies
        
        # Determine which sides are available for spawning
        available_sides = []
        if game_state.camera_pos[1] > margin:  # Not at top edge
            available_sides.append("top")
        if game_state.camera_pos[1] + config.HEIGHT < config.LEVEL_HEIGHT - margin:  # Not at bottom edge
            available_sides.append("bottom")
        if game_state.camera_pos[0] > margin:  # Not at left edge
            available_sides.append("left")
        if game_state.camera_pos[0] + config.WIDTH < config.LEVEL_WIDTH - margin:  # Not at right edge
            available_sides.append("right")
        
        if not available_sides:
            return  # No available sides to spawn enemies
        
        side = random.choice(available_sides)
        
        if side == "top":
            x = random.randint(int(game_state.camera_pos[0]), int(game_state.camera_pos[0] + config.WIDTH))
            y = game_state.camera_pos[1] - margin
        elif side == "bottom":
            x = random.randint(int(game_state.camera_pos[0]), int(game_state.camera_pos[0] + config.WIDTH))
            y = game_state.camera_pos[1] + config.HEIGHT + margin
        elif side == "left":
            x = game_state.camera_pos[0] - margin
            y = random.randint(int(game_state.camera_pos[1]), int(game_state.camera_pos[1] + config.HEIGHT))
        else:  # right
            x = game_state.camera_pos[0] + config.WIDTH + margin
            y = random.randint(int(game_state.camera_pos[1]), int(game_state.camera_pos[1] + config.HEIGHT))
        
        # Ensure spawn position is within level bounds
        x = max(game_state.enemy_size // 2, min(x, config.LEVEL_WIDTH - game_state.enemy_size // 2))
        y = max(game_state.enemy_size // 2, min(y, config.LEVEL_HEIGHT - game_state.enemy_size // 2))
        
        new_enemy = Enemy(x, y, game_state)
        game_state.add_enemy(new_enemy)

def check_player_collision(game_state):
    for enemy in game_state.enemies:
        enemy_rect = pygame.Rect(enemy.pos.x, enemy.pos.y, game_state.enemy_size, game_state.enemy_size)
        if game_state.player_rect.colliderect(enemy_rect):
            # Calculate direction from player to enemy
            direction = Vector2(enemy.pos.x - game_state.player_pos[0], 
                                enemy.pos.y - game_state.player_pos[1])
            if direction.length() > 0:
                direction = direction.normalize()
            
            # Move enemy away from player
            push_strength = max(game_state.enemy_size, game_state.player_size)
            enemy.pos.x += direction.x * push_strength
            enemy.pos.y += direction.y * push_strength
            
            # Change enemy direction
            enemy.direction = direction  # Move away from player
            enemy.change_state()  # Immediately change state after collision

            return False
    return False