"""
Bullet module.
"""
import pygame
from typing import List, Dict, Optional, Tuple
from config import (
    BULLET_SPEED, BULLET_DAMAGE, BULLET_SIZE,
    ENEMY_BULLET_SPEED, ENEMY_BULLET_DAMAGE, ENEMY_BULLET_SIZE
)
from entities import EntityType
from components import (
    TransformComponent, VelocityComponent, DamageComponent,
    BulletComponent, LifetimeComponent, CollisionComponent
)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, dx: float, dy: float, damage: int,
                 is_enemy: bool = False, size: int = BULLET_SIZE):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill((255, 255, 0) if is_enemy else (0, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Calculate velocity
        length = (dx ** 2 + dy ** 2) ** 0.5
        if length > 0:
            self.velocity_x = (dx / length) * (ENEMY_BULLET_SPEED if is_enemy else BULLET_SPEED)
            self.velocity_y = (dy / length) * (ENEMY_BULLET_SPEED if is_enemy else BULLET_SPEED)
        else:
            self.velocity_x = 0
            self.velocity_y = 0
        
        # Bullet properties
        self.damage = damage
        self.is_enemy = is_enemy
        self.lifetime = 120  # Frames before bullet disappears
    
    def update(self, world_manager):
        """Update bullet position and check collisions."""
        # Update position
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Check collisions with world
        if self._check_world_collision(world_manager):
            self.kill()
            return
        
        # Update lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
    
    def _check_world_collision(self, world_manager) -> bool:
        """Check if bullet collides with world tiles."""
        # Get current zone and surrounding zones
        zone_x = self.rect.x // world_manager.zone_size
        zone_y = self.rect.y // world_manager.zone_size
        
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
                        if self.rect.colliderect(tile_rect):
                            return True
        
        return False

class BulletManager:
    """Manages bullet creation and lifecycle."""
    
    def __init__(self, entity_manager):
        """Initialize the bullet manager."""
        self.entity_manager = entity_manager
        self.bullets = pygame.sprite.Group()  # Initialize bullets group

    def create_bullet(self, x, y, dx, dy, damage, is_enemy=False, size=None):
        """Create a new bullet entity with all required components."""
        if size is None:
            size = ENEMY_BULLET_SIZE if is_enemy else BULLET_SIZE

        # Create bullet entity
        entity = self.entity_manager.create_entity(EntityType.BULLET)
        
        # Add transform component
        transform = TransformComponent(entity)
        transform.x = x
        transform.y = y
        entity.add_component(transform)
        
        # Calculate and add velocity component
        length = (dx**2 + dy**2) ** 0.5
        if length > 0:
            vx = (dx / length) * (ENEMY_BULLET_SPEED if is_enemy else BULLET_SPEED)
            vy = (dy / length) * (ENEMY_BULLET_SPEED if is_enemy else BULLET_SPEED)
        else:
            vx, vy = 0, 0
        entity.add_component(VelocityComponent(vx, vy))
        
        # Add other components
        entity.add_component(DamageComponent(damage))
        entity.add_component(BulletComponent(is_enemy))
        entity.add_component(LifetimeComponent(frames_left=120))
        
        # Add collision component
        collision = CollisionComponent(entity)
        collision.width = size
        collision.height = size
        entity.add_component(collision)
        
        self.entity_manager.add_entity(entity)
        
        return entity
    
    def update(self, world_manager):
        """Update all bullets."""
        for bullet in self.bullets:
            bullet.update(world_manager)
    
    def draw(self, screen: pygame.Surface, camera_x: int, camera_y: int):
        """Draw all bullets."""
        for bullet in self.bullets:
            screen.blit(bullet.image, (
                bullet.rect.x - camera_x + screen.get_width() // 2,
                bullet.rect.y - camera_y + screen.get_height() // 2
            ))
    
    def get_bullets(self) -> pygame.sprite.Group:
        """Get the bullet sprite group."""
        return self.bullets 