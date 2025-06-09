import pygame
import math
from pygame.locals import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, speed, damage, is_player, size=5, color=(255, 255, 255)):
        super().__init__()
        if isinstance(size, (tuple, list)):
            width, height = size
        else:
            width = height = size
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (width//2, height//2), min(width, height)//2)
        self.rect = self.image.get_rect(center=start_pos)
        self.pos = pygame.math.Vector2(start_pos)
        self.vel = pygame.math.Vector2(target_pos) - self.pos
        if self.vel.length() > 0:
            self.vel = self.vel.normalize() * speed
        self.damage = damage
        self.is_player = is_player

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos

class BulletManager:
    def __init__(self, bullets_group):
        self.bullets = bullets_group

    def create_bullet(self, start_pos, target_pos, speed=10, damage=1, is_player=True, size=5, color=(255, 255, 255)):
        """Create a new bullet."""
        bullet = Bullet(start_pos, target_pos, speed, damage, is_player, size, color)
        self.bullets.add(bullet)
        return bullet

    def update(self):
        """Update all bullets and remove those that are off screen."""
        screen_rect = pygame.display.get_surface().get_rect()
        for bullet in self.bullets:
            bullet.update()
            # Remove bullets that are off screen
            if not screen_rect.colliderect(bullet.rect):
                bullet.kill()

    def draw(self, screen):
        """Draw all bullets."""
        self.bullets.draw(screen)

    def get_bullets(self):
        """Get the bullets sprite group."""
        return self.bullets

    def clear(self):
        """Remove all bullets."""
        self.bullets.empty() 