import pytest
import pygame
from bullets import Bullet

@pytest.fixture
def bullet():
    pygame.init()
    return Bullet(100, 100, 1, 1, 10)

def test_bullet_initialization(bullet):
    assert bullet.rect.x == 100
    assert bullet.rect.y == 100
    assert bullet.damage == 10
    assert bullet.speed > 0

def test_bullet_movement(bullet):
    initial_x = bullet.rect.x
    initial_y = bullet.rect.y
    
    bullet.update()
    assert bullet.rect.x != initial_x or bullet.rect.y != initial_y

def test_bullet_lifetime(bullet):
    # Simulate bullet moving off screen
    bullet.rect.x = -100
    bullet.rect.y = -100
    assert bullet.should_remove()

def test_bullet_collision(bullet):
    # Create a test rect for collision
    test_rect = pygame.Rect(100, 100, 10, 10)
    assert bullet.rect.colliderect(test_rect) 