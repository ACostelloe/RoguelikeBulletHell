"""
Enemy management module.
"""
import pygame
import math
import random
import os
from sprite_animator import SpriteAnimator
from player import Player
from typing import Tuple, List, Optional, Dict, Any
from config import (
    ENEMY_BASE_HEALTH, ENEMY_BASE_DAMAGE, ENEMY_BASE_SPEED,
    ENEMY_SPAWN_RATE, RED, ENEMY_BULLET_DAMAGE, ENEMY_SHOOT_DELAY,
    ENEMY_SPEED, ENEMY_HEALTH, SCREEN_WIDTH, SCREEN_HEIGHT
)
from logger import logger
from bullets import BulletManager
from world_manager import WorldManager
from entities import Entity, EntityType
from enemy_ai import EnemyBehavior, EnemyState
from status_effects import create_poison_effect, create_burn_effect, create_slow_effect
import traceback

class Enemy(Entity):
    _next_id = 0  # Class variable to track next available ID
    
    def __init__(self, x: int, y: int, enemy_type: str, biome: str):
        super().__init__(EntityType.ENEMY, x, y, 32, 32)
        self.id = Enemy._next_id
        Enemy._next_id += 1
        
        # Enemy-specific properties
        self.enemy_type = enemy_type
        self.biome = biome
        self.health = ENEMY_HEALTH
        self.max_health = ENEMY_HEALTH
        self.speed = ENEMY_SPEED
        self.damage = ENEMY_BULLET_DAMAGE
        self.contact_damage = 1  # Damage dealt on contact with player
        self.attack_delay = ENEMY_SHOOT_DELAY
        self.attack_cooldown = 0
        self.detection_range = 200
        self.gravity = 0.5
        self.last_collision = None
        self.collision_count = 0
        
        # Movement properties
        self.patrol_points = []
        self.current_patrol_index = 0
        self.patrol_speed = 2
        self.patrol_wait_time = 0
        self.patrol_wait_duration = 60  # Frames to wait at patrol point
        
        # Initialize behavior
        self.behavior = EnemyBehavior(
            detection_range=200,
            attack_range=50,
            flee_health_threshold=0.3,
            patrol_points=[],
            attack_cooldown=1.0,
            movement_speed=100,
            attack_damage=self.damage
        )
        
        # Set up event handlers
        self.add_event_handler("death", self._on_death)
        self.add_event_handler("damage", self._on_damage)
        
        logger.info(f"Enemy {self.id} created at ({x}, {y})")
        
    def _generate_patrol_points(self):
        """Generate patrol points around the enemy's initial position."""
        center_x = self.rect.centerx
        center_y = self.rect.centery
        radius = 100
        
        # Generate 4 patrol points in a square pattern
        self.patrol_points = [
            (center_x - radius, center_y - radius),
            (center_x + radius, center_y - radius),
            (center_x + radius, center_y + radius),
            (center_x - radius, center_y + radius)
        ]
        
    def update(self, dt):
        """Update enemy state."""
        # Get platforms from world manager
        platforms = self.world_manager.get_platforms() if hasattr(self, 'world_manager') else []
        
        # Update position
        self.move(self.velocity_x, self.velocity_y)
        
        # Keep in bounds
        self._handle_screen_bounds()
        
        # Check platform collisions
        self._handle_platform_collisions(platforms)
        
        # Attack if cooldown is ready
        if self.attack_cooldown <= 0:
            self._attack()
            self.attack_cooldown = self.attack_delay
        else:
            self.attack_cooldown -= 1
        
        # Apply gravity
        self.apply_gravity()
        
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
                        self.velocity_y = 0
                        self.on_ground = True
                        self.last_collision = 'vertical_bottom'
                    else:
                        self.rect.top = platform.rect.bottom
                        self.velocity_y = 0
                        self.last_collision = 'vertical_top'
                self.collision_count += 1
                    
    def _handle_screen_bounds(self):
        """Handle enemy collision with screen boundaries."""
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity_x *= -1
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.velocity_x *= -1
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y *= -1
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y *= -1
            
    def _handle_platform_collisions(self, platforms):
        """Handle collisions with platforms."""
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
                    self.velocity_x *= -1
                else:
                    # Vertical collision
                    if self.rect.centery < platform.rect.centery:
                        self.rect.bottom = platform.rect.top
                    else:
                        self.rect.top = platform.rect.bottom
                    self.velocity_y *= -1
                    
    def _attack(self):
        """Attack the player if in range."""
        if not hasattr(self, 'player') or not hasattr(self, 'bullet_manager'):
            return
            
        # Calculate distance to player
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        # Only attack if in range
        if distance <= self.detection_range:
            self.bullet_manager.create_bullet(
                self.rect.centerx,
                self.rect.centery,
                dx,
                dy,
                self.damage,
                is_enemy=True
            )
            logger.debug(f"Enemy {self.id} shot at player")

    def set_world_manager(self, world_manager):
        """Set the world manager reference."""
        self.world_manager = world_manager

    def set_player(self, player):
        """Set the player reference."""
        self.player = player

    def set_bullet_manager(self, bullet_manager):
        """Set the bullet manager reference."""
        self.bullet_manager = bullet_manager

    def draw(self, screen):
        """Draw the enemy and its health bar."""
        # Draw enemy body
        pygame.draw.rect(screen, (255, 0, 0), self.rect)
        
        # Draw health bar
        health_width = (self.health / self.max_health) * self.rect.width
        pygame.draw.rect(screen, (0, 255, 0), 
                        (self.rect.x, self.rect.y - 10, health_width, 5))
        
        # Draw detection range (for debugging)
        pygame.draw.circle(screen, (255, 255, 255), 
                         self.rect.center, self.detection_range, 1)
        
        # Draw debug info
        if self.last_collision:
            font = pygame.font.Font(None, 20)
            debug_text = f"ID: {self.id} | Collision: {self.last_collision} | Count: {self.collision_count}"
            text_surface = font.render(debug_text, True, (255, 255, 255))
            screen.blit(text_surface, (self.rect.x, self.rect.y - 20))

    def _on_death(self) -> None:
        """Handle enemy death."""
        self.drop_loot()
            
    def _on_damage(self, amount: int) -> None:
        """Handle taking damage."""
        # Check if we should flee
        if self.health and self.health <= self.max_health * self.behavior.flee_health_threshold:
            self.behavior.state = EnemyState.FLEE
            
    def drop_loot(self) -> None:
        """Drop loot when the enemy is defeated."""
        try:
            # Create loot entity
            loot = self.entity_manager.create_entity(EntityType.ITEM, "loot")
            
            # Add transform component
            transform = loot.get_component(TransformComponent)
            transform.x = self.transform.x
            transform.y = self.transform.y
            
            # Add item component
            item = ItemComponent(loot)
            item.item_type = random.choice(["health", "ammo", "powerup"])
            item.value = random.randint(1, 5)
            loot.add_component(item)
            
            # Add to game world
            self.game_world.add_entity(loot)
            
        except Exception as e:
            logger.error(f"Error dropping loot: {str(e)}")
            logger.error(traceback.format_exc())

    def set_entity_manager(self, entity_manager):
        """Set the entity manager reference."""
        self.entity_manager = entity_manager

    def set_patrol_points(self, points: List[Tuple[int, int]]) -> None:
        """Set patrol points for the enemy."""
        self.behavior.patrol_points = points
        self.current_patrol_index = 0

    def stun(self, duration: float) -> None:
        """Stun the enemy for a duration."""
        self.behavior.stun(duration, self.current_time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert enemy to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "enemy_type": self.enemy_type,
            "biome": self.biome,
            "loot_chance": self.loot_chance,
            "current_time": self.current_time,
            "behavior": self.behavior.to_dict()
        })
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Enemy':
        """Create enemy from dictionary."""
        enemy = cls(
            data["x"],
            data["y"],
            data["enemy_type"],
            data["biome"]
        )
        
        # Restore basic properties
        enemy.health = data.get("health")
        enemy.max_health = data.get("max_health")
        enemy.damage = data.get("damage")
        enemy.contact_damage = data.get("contact_damage")
        enemy.velocity_x = data.get("velocity_x", 0)
        enemy.velocity_y = data.get("velocity_y", 0)
        enemy.zone_id = data.get("zone_id")
        enemy.loot_chance = data.get("loot_chance", 0.3)
        enemy.current_time = data.get("current_time", 0)
        
        # Restore behavior
        enemy.behavior = EnemyBehavior.from_dict(data["behavior"])
        
        # Restore status effects
        for effect_data in data.get("status_effects", []):
            effect = StatusEffect(
                name=effect_data["name"],
                duration=effect_data["duration"],
                tick_func=lambda dt, e: None,  # Default empty tick function
                data=effect_data["data"]
            )
            effect.elapsed = effect_data["elapsed"]
            enemy.status_effects.append(effect)
            
        return enemy

class EnemyManager:
    def __init__(self, screen_width: int, screen_height: int):
        self.enemies = pygame.sprite.Group()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.wave_number = 1
        self.enemies_remaining = 5
        self.max_enemies_on_screen = 3
        self.spawn_timer = 0
        self.spawn_delay = 120
        self.boss_wave_interval = 5
        self.spawn_radius = 100
        self.wave_timer = 0
        self.wave_delay = 180
        self.enemies_per_wave = ENEMY_SPAWN_RATE
        self.difficulty_scaling = 1.0
        logger.info("Enemy manager initialized")
        self.enemy_types = {
            "basic": {
                "health": ENEMY_HEALTH,
                "speed": ENEMY_SPEED,
                "bullet_damage": ENEMY_BULLET_DAMAGE,
                "shoot_delay": ENEMY_SHOOT_DELAY
            },
            "fast": {
                "health": ENEMY_HEALTH * 0.7,
                "speed": ENEMY_SPEED * 1.5,
                "bullet_damage": ENEMY_BULLET_DAMAGE * 0.7,
                "shoot_delay": ENEMY_SHOOT_DELAY * 0.7
            },
            "tank": {
                "health": ENEMY_HEALTH * 2,
                "speed": ENEMY_SPEED * 0.7,
                "bullet_damage": ENEMY_BULLET_DAMAGE * 1.5,
                "shoot_delay": ENEMY_SHOOT_DELAY * 1.5
            }
        }

    def create_enemy(self, pos, enemy_type, wave_number):
        """Create a new enemy at the specified position."""
        if len(self.enemies) >= self.max_enemies_on_screen:
            return None
            
        enemy = Enemy(pos[0], pos[1], enemy_type, "")
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

    def _get_spawn_position(self, player, screen_width, screen_height):
        """Get a valid spawn position for an enemy."""
        if not player:
            # If no player, spawn at random position
            x = random.randint(0, screen_width - 30)
            y = random.randint(0, screen_height - 30)
            return (x, y)

        # Try to find a position outside the player's view
        for _ in range(10):  # Try up to 10 times
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(self.spawn_radius, self.spawn_radius * 2)
            x = player.rect.centerx + math.cos(angle) * distance
            y = player.rect.centery + math.sin(angle) * distance
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

    def _spawn_enemy(self, player_position, screen_width, screen_height):
        # Unpack player position tuple
        player_x, player_y = player_position
        angle = random.uniform(0, 2 * math.pi)
        distance = 300
        x = player_x + math.cos(angle) * distance
        y = player_y + math.sin(angle) * distance
        enemy_type = random.choice(self.enemy_types)
        biome = "forest"
        print(f"[ENEMY SPAWN] Spawning {enemy_type} at ({x}, {y})")
        enemy = Enemy(x, y, enemy_type, biome)
        self.enemies.add(enemy)

    def update(self, player_rect, world_manager, bullet_manager, screen_width, screen_height):
        """Update all enemies."""
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
                self._spawn_enemy(self.player_rect.center, screen_width, screen_height)
        
        # Update all enemies
        for enemy in self.enemies:
            enemy.update(dt)

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
        logger.debug("All enemies cleared")

    def spawn_enemy(self, player_position, screen_width, screen_height):
        self._spawn_enemy(player_position, screen_width, screen_height)

    def update_enemy_spawns(self, enemy_spawns: List[Dict]):
        """Update enemy manager with new spawns."""
        # Clear existing enemies
        self.enemies.empty()
        
        # Create new enemies from spawns
        for spawn in enemy_spawns:
            enemy = Enemy(
                spawn["x"],
                spawn["y"],
                spawn["type"],
                spawn["biome"]
            )
            
            # Set patrol points if provided
            if "patrol_points" in spawn:
                enemy.set_patrol_points(spawn["patrol_points"])
            
            self.enemies.add(enemy)

    def _update_patrol(self, enemy: Enemy):
        """Update patrol movement."""
        if not enemy.patrol_points:
            return
        
        # Get current target point
        target = enemy.patrol_points[enemy.current_patrol_index]
        
        # Calculate direction to target
        dx = target[0] - enemy.rect.centerx
        dy = target[1] - enemy.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        # Move towards target
        if distance > 5:  # Small threshold to prevent jittering
            enemy.velocity_x = (dx / distance) * enemy.speed
            enemy.velocity_y = (dy / distance) * enemy.speed
        else:
            # Reached target, move to next point
            enemy.current_patrol_index = (enemy.current_patrol_index + 1) % len(enemy.patrol_points)

    def _check_collisions(self, enemy: Enemy, world_manager):
        """Check collisions with the world."""
        # Get current zone and surrounding zones
        zone_x = enemy.rect.x // world_manager.zone_size
        zone_y = enemy.rect.y // world_manager.zone_size
        
        # Check collisions with tiles in current and adjacent zones
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                check_zone_x = zone_x + dx
                check_zone_y = zone_y + dy
                
                if (check_zone_x, check_zone_y) in world_manager.active_zones:
                    zone = world_manager.active_zones[(check_zone_x, check_zone_y)]
                    
                    # Check collisions with tiles
                    for tile in zone["tiles"]:
                        tile_rect = pygame.Rect(tile["x"], tile["y"], 32, 32)
                        
                        # Horizontal collision
                        if enemy.velocity_x != 0:
                            if enemy.rect.colliderect(tile_rect):
                                if enemy.velocity_x > 0:
                                    enemy.rect.right = tile_rect.left
                                else:
                                    enemy.rect.left = tile_rect.right
                                enemy.velocity_x = 0
                        
                        # Vertical collision
                        if enemy.velocity_y != 0:
                            if enemy.rect.colliderect(tile_rect):
                                if enemy.velocity_y > 0:
                                    enemy.rect.bottom = tile_rect.top
                                else:
                                    enemy.rect.top = tile_rect.bottom
                                enemy.velocity_y = 0
    
    def _attack(self, enemy: Enemy, bullet_manager: BulletManager):
        """Attack the target."""
        current_time = pygame.time.get_ticks()
        if current_time - enemy.last_shot >= enemy.shoot_delay:
            # Calculate direction to target
            dx = enemy.target.rect.centerx - enemy.rect.centerx
            dy = enemy.target.rect.centery - enemy.rect.centery
            
            # Create bullet
            bullet_manager.create_bullet(
                enemy.rect.centerx,
                enemy.rect.centery,
                dx,
                dy,
                enemy.bullet_damage,
                is_enemy=True
            )
            
            enemy.last_shot = current_time
    
    def take_damage(self, enemy: Enemy, amount: int):
        """Take damage and return True if enemy is dead."""
        enemy.health -= amount
        return enemy.health <= 0
    
    def set_patrol_points(self, enemy: Enemy, points: List[Tuple[int, int]]):
        """Set the patrol points for this enemy."""
        enemy.set_patrol_points(points)
        enemy.current_patrol_index = 0 