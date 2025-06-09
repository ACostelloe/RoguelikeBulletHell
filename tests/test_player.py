import pytest
import pygame
from player import Player

@pytest.fixture
def player():
    pygame.init()
    return Player(100, 100)

def test_player_initialization(player):
    assert player.rect.x == 100
    assert player.rect.y == 100
    assert player.health > 0
    assert player.speed > 0

def test_player_movement(player):
    initial_x = player.rect.x
    initial_y = player.rect.y
    
    # Test right movement
    player.move_right()
    assert player.rect.x > initial_x
    
    # Test left movement
    player.rect.x = initial_x
    player.move_left()
    assert player.rect.x < initial_x
    
    # Test up movement
    player.rect.y = initial_y
    player.move_up()
    assert player.rect.y < initial_y
    
    # Test down movement
    player.rect.y = initial_y
    player.move_down()
    assert player.rect.y > initial_y

def test_player_health(player):
    initial_health = player.health
    player.take_damage(10)
    assert player.health == initial_health - 10
    assert not player.is_dead()

def test_player_death(player):
    player.health = 1
    player.take_damage(10)
    assert player.is_dead() 