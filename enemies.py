import pygame
import math
import random
import os
from sprite_animator import SpriteAnimator
from player import Player

class Enemy(pygame.sprite.Sprite):
    _next_id = 0  # Class variable to track next available ID
    
    def __init__(self, x, y, enemy_type='basic'):
        super().__init__()
        self.id = Enemy._next_id
        Enemy._next_id += 1
        
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        
        # Create a simple rectangle sprite
        self.image = pygame.Surface((32, 32))
        if enemy_type == 'basic':
            self.image.fill((255, 0, 0))  # Red for basic
        elif enemy_type == 'fast':
            self.image.fill((255, 165, 0))  # Orange for fast
        elif enemy_type == 'tank':
            self.image.fill((128, 0, 128))  # Purple for tank
        elif enemy_type == 'shooter':
            self.image.fill((0, 0, 255))  # Blue for shooter
        elif enemy_type == 'boss':
            self.image.fill((255, 0, 255))  # Magenta for boss
        
        self.rect = self.image.get_rect(center=(x, y))
        self.move_speed = 2
        self.health = 10
        self.max_health = 10
        self.state = 'idle'
        
        # Movement properties
        self.vel_x = 0
        self.vel_y = 0
        self.gravity = 0.8
        self.on_ground = False
        
        # Combat properties
        self.damage = 10
        self.attack_range = 50
        self.detection_range = 200
        self.retreat_health = 20
        
        # State properties
        self.current_state = 'idle'
        self.state_timer = 0
        self.facing_right = True
        
        # Debug properties
        self.last_collision = None
        self.collision_count = 0
        
        # Setup enemy type specific properties
        self._setup_enemy()
        
    def _setup_enemy(self):
        """Setup enemy properties based on type."""
        if self.enemy_type == 'basic':
            self.health = 50
            self.max_health = 50
            self.damage = 10
            self.attack_range = 50
            self.detection_range = 200
            self.retreat_health = 20
            self.move_speed = 2
        elif self.enemy_type == 'fast':
            self.health = 30
            self.max_health = 30
            self.damage = 5
            self.attack_range = 40
            self.detection_range = 250
            self.retreat_health = 10
            self.move_speed = 4
        elif self.enemy_type == 'tank':
            self.health = 200
            self.max_health = 200
            self.damage = 20
            self.attack_range = 60
            self.detection_range = 150
            self.retreat_health = 50
            self.move_speed = 1
        elif self.enemy_type == 'shooter':
            self.health = 40
            self.max_health = 40
            self.damage = 15
            self.attack_range = 300
            self.detection_range = 400
            self.retreat_health = 15
            self.move_speed = 1.5
        elif self.enemy_type == 'boss':
            self.health = 500
            self.max_health = 500
            self.damage = 30
            self.attack_range = 100
            self.detection_range = 500
            self.retreat_health = 100
            self.move_speed = 1.5
            
    def update(self, player_rect, platforms, bullet_manager, screen_width, screen_height):
        # Simple AI: move toward player
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        
        # Store old position for collision resolution
        old_rect = self.rect.copy()
        
        # Update movement based on state
        if self.current_state == 'retreat':
            # Move away from player
            self.rect.x -= int(self.move_speed * dx / dist)
            self.rect.y -= int(self.move_speed * dy / dist)
        else:
            # Move toward player
            self.rect.x += int(self.move_speed * dx / dist)
            self.rect.y += int(self.move_speed * dy / dist)
        
        # Keep enemy in bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
        
        # Update state based on health and distance
        if self.health <= self.retreat_health:
            self.current_state = 'retreat'
        elif dist > self.attack_range:
            self.current_state = 'chase'
        else:
            self.current_state = 'attack'
            if self.enemy_type == 'shooter':
                self._attack(player_rect)
        
        # Apply gravity
        self.vel_y += self.gravity
        
        # Limit fall speed
        if self.vel_y > 15:  # Max fall speed
            self.vel_y = 15
        
        # Platform collisions
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Calculate overlap
                dx = min(self.rect.right - platform.rect.left, platform.rect.right - self.rect.left)
                dy = min(self.rect.bottom - platform.rect.top, platform.rect.bottom - self.rect.top)
                
                # Resolve collision based on smallest overlap
                if dx < dy:
                    # Horizontal collision
                    if self.rect.centerx < platform.rect.centerx:
                        self.rect.right = platform.rect.left
                    else:
                        self.rect.left = platform.rect.right
                    self.last_collision = 'horizontal'
                else:
                    # Vertical collision
                    if self.rect.centery < platform.rect.centery:
                        self.rect.bottom = platform.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                        self.last_collision = 'vertical_bottom'
                    else:
                        self.rect.top = platform.rect.bottom
                        self.vel_y = 0
                        self.last_collision = 'vertical_top'
                self.collision_count += 1
                    
    def _attack(self, player_rect):
        """Perform attack on player."""
        if self.enemy_type == 'shooter':
            # Shoot at player
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            distance = (dx**2 + dy**2)**0.5
            if distance > 0:
                dx /= distance
                dy /= distance
                # Create bullet
                # TODO: Implement bullet creation
        else:
            # Melee attack
            if self.rect.colliderect(player_rect):
                # TODO: Implement player damage
                pass
            
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # Draw health bar
        health_ratio = self.health / self.max_health
        bar_width = self.rect.width
        bar_height = 4
        bar_x = self.rect.x
        bar_y = self.rect.y - bar_height - 2
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
        
        # Draw debug info
        if self.last_collision:
            font = pygame.font.Font(None, 20)
            debug_text = f"ID: {self.id} | Collision: {self.last_collision} | Count: {self.collision_count}"
            text_surface = font.render(debug_text, True, (255, 255, 255))
            screen.blit(text_surface, (self.rect.x, self.rect.y - 20))

class EnemyManager:
    def __init__(self, screen_width, screen_height):
        self.enemies = pygame.sprite.Group()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player_rect = None
        self.wave_number = 1
        self.enemies_remaining = 5
        self.max_enemies_on_screen = 3
        self.spawn_timer = 0
        self.spawn_delay = 120
        self.boss_wave_interval = 5
        self.spawn_radius = 100
        self.wave_timer = 0
        self.wave_delay = 180
        self.enemies_per_wave = 5
        self.difficulty_scaling = 1.0

    def create_enemy(self, pos, enemy_type, wave_number):
        """Create a new enemy at the specified position."""
        if len(self.enemies) >= self.max_enemies_on_screen:
            return None
            
        enemy = Enemy(pos[0], pos[1], enemy_type)
        self.enemies.add(enemy)
        return enemy

    def _select_enemy_type(self):
        """Select enemy type based on wave number."""
        if self.wave_number % self.boss_wave_interval == 0:
            return 'boss'
        
        # Basic enemy types for early waves
        if self.wave_number <= 3:
            return 'basic'
        
        # Add more variety in later waves
        enemy_types = ['basic', 'fast', 'tank']
        weights = [0.6, 0.3, 0.1]  # 60% basic, 30% fast, 10% tank
        
        # Adjust weights based on wave number
        if self.wave_number > 5:
            weights = [0.4, 0.4, 0.2]  # More fast enemies and tanks
        
        return random.choices(enemy_types, weights=weights)[0]

    def _get_spawn_position(self, player_rect, screen_width, screen_height):
        """Get a valid spawn position for an enemy."""
        if not player_rect:
            # If no player rect, spawn at random position
            x = random.randint(0, screen_width - 30)
            y = random.randint(0, screen_height - 30)
            return (x, y)

        # Try to find a position outside the player's view
        for _ in range(10):  # Try up to 10 times
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(self.spawn_radius, self.spawn_radius * 2)
            x = player_rect.centerx + math.cos(angle) * distance
            y = player_rect.centery + math.sin(angle) * distance
            
            # Ensure position is within screen bounds
            x = max(0, min(x, screen_width - 30))
            y = max(0, min(y, screen_height - 30))
            
            # Check if position is far enough from other enemies
            too_close = False
            for enemy in self.enemies:
                dx = enemy.rect.centerx - x
                dy = enemy.rect.centery - y
                if math.sqrt(dx * dx + dy * dy) < 100:  # Increased minimum distance
                    too_close = True
                    break
            if not too_close:
                return (x, y)
        return None  # No valid position found

    def _spawn_enemy(self, screen_width, screen_height):
        """Spawn a new enemy if conditions are met."""
        if len(self.enemies) < self.max_enemies_on_screen:
            enemy_type = self._select_enemy_type()
            spawn_pos = self._get_spawn_position(self.player_rect, screen_width, screen_height)
            if spawn_pos:
                self.create_enemy(spawn_pos, enemy_type, self.wave_number)
                self.enemies_remaining -= 1

    def update(self, player_rect, platforms, bullet_manager, screen_width, screen_height):
        """Update all enemies."""
        self.player_rect = player_rect  # Update player_rect reference
        
        # Update wave timer
        self.wave_timer += 1
        if self.wave_timer >= self.wave_delay:
            self.wave_timer = 0
            self.wave_number += 1
            self.enemies_remaining = self.enemies_per_wave
            self.difficulty_scaling += 0.1
        
        # Update spawn timer
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_timer = 0
            if self.enemies_remaining > 0:
                self._spawn_enemy(screen_width, screen_height)
        
        # Update all enemies
        for enemy in self.enemies:
            enemy.update(player_rect, platforms, bullet_manager, screen_width, screen_height)

    def draw(self, screen):
        """Draw all enemies."""
        for enemy in self.enemies:
            enemy.draw(screen)

    def get_enemies(self):
        """Get the sprite group of enemies."""
        return self.enemies

    def clear(self):
        """Clear all enemies."""
        self.enemies.empty()
        self.wave_number = 1
        self.enemies_remaining = self.enemies_per_wave
        self.difficulty_scaling = 1.0

    def spawn_enemy(self, player_rect, screen_width, screen_height):
        """Spawn a new enemy."""
        self.player_rect = player_rect  # Update player_rect reference
        self._spawn_enemy(screen_width, screen_height) 