import pytest
import pygame
from bullets import Bullet

class MockWorldManager:
    def __init__(self):
        self.zone_size = 1000
        self.active_zones = {}

@pytest.fixture
def bullet():
    pygame.init()
    return Bullet(100, 100, 1, 1, 10)

@pytest.fixture
def world_manager():
    return MockWorldManager()

def test_bullet_initialization(bullet):
    assert bullet.rect.x == 100
    assert bullet.rect.y == 100
    assert bullet.damage == 10
    assert bullet.velocity_x != 0 or bullet.velocity_y != 0

def test_bullet_movement(bullet, world_manager):
    initial_x = bullet.rect.x
    initial_y = bullet.rect.y
    
    bullet.update(world_manager)
    assert bullet.rect.x != initial_x or bullet.rect.y != initial_y

def test_bullet_lifetime(bullet, world_manager):
    # Simulate bullet moving off screen
    bullet.rect.x = -100
    bullet.rect.y = -100
    bullet.lifetime = 0
    bullet.update(world_manager)
    assert not bullet.alive()  # Check if bullet was killed

def test_bullet_collision(bullet):
    # Create a test rect for collision
    test_rect = pygame.Rect(100, 100, 10, 10)
    assert bullet.rect.colliderect(test_rect) 