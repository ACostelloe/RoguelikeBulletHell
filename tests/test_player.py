import pytest
import pygame
from player import Player, PlayerStats, PlayerAbilities, Item
from components import HealthComponent, TransformComponent, SpriteComponent
from entities import Entity, EntityType
from pygame.math import Vector2
from bullets import Bullet
import os
from collections import defaultdict

@pytest.fixture
def player():
    pygame.init()
    return Player(100, 100)

def test_player_initialization(player):
    assert player.rect.x == 100
    assert player.rect.y == 100
    assert player.stats.max_health > 0
    assert player.stats.move_speed > 0

def test_player_movement(player):
    initial_x = player.rect.x
    initial_y = player.rect.y
    
    # Test movement using move_direction
    player.move_direction.x = 1  # Move right
    player.update(0.016)  # Update with 16ms delta time
    assert player.rect.x > initial_x
    
    # Reset position
    player.rect.x = initial_x
    player.rect.y = initial_y
    transform = player.get_component(TransformComponent)
    transform.x = initial_x
    transform.y = initial_y
    
    # Test movement in opposite direction
    player.move_direction.x = -1  # Move left
    player.update(0.016)
    assert player.rect.x < initial_x

def test_player_health(player):
    # Remove player data file for a clean state
    try:
        os.remove("data/player_data.json")
    except FileNotFoundError:
        pass
    player = Player(100, 100)
    initial_health = player.stats.max_health
    # The default defense is 5.0, so damage taken = max(1, amount - defense)
    damage = 10
    expected_damage = max(1, damage - player.stats.defense)
    player.take_damage(damage)
    health_component = player.get_component(HealthComponent)
    assert health_component.current_health == initial_health - expected_damage
    assert not health_component.is_dead()

def test_player_death(player):
    health_component = player.get_component(HealthComponent)
    health_component.current_health = 1
    player.take_damage(10)
    assert health_component.is_dead()

def test_player_stats(player):
    # Remove player data file for a clean state
    try:
        os.remove("data/player_data.json")
    except FileNotFoundError:
        pass
    player = Player(100, 100)
    # Test initial stats
    assert player.stats.level == 1
    assert player.stats.experience == 0.0
    assert player.stats.skill_points == 0
    
    # Test experience gain
    player.gain_experience(50.0)
    assert player.stats.experience == 50.0
    assert not player.stats.gain_experience(40.0)  # Should not level up yet (90 < 100)
    
    # Test level up
    assert player.stats.gain_experience(20.0)  # Should level up (90 + 20 > 100)
    assert player.stats.level == 2
    assert player.stats.skill_points == 1

def test_player_abilities(player):
    # Test initial state
    assert player.abilities.can_dash()
    assert player.abilities.can_use_ultimate()
    
    # Test dash cooldown
    player.abilities.dash_cooldown = 1.0
    assert not player.abilities.can_dash()
    
    # Test ultimate cooldown
    player.abilities.ultimate_cooldown = 1.0
    assert not player.abilities.can_use_ultimate()
    
    # Test cooldown update
    player.abilities.update(0.5)
    assert player.abilities.dash_cooldown == 0.5
    assert player.abilities.ultimate_cooldown == 0.5 

def test_player_inventory(player):
    """Test inventory management."""
    # Create test items
    sword = Item("Test Sword", "A test weapon", "weapon", "common", 1, {"damage": 5.0})
    shield = Item("Test Shield", "A test armor", "armor", "common", 1, {"defense": 3.0})
    
    # Test adding items
    assert player.add_item(sword)
    assert player.add_item(shield)
    assert len(player.inventory) == 2
    
    # Test removing items
    removed_item = player.remove_item("Test Sword")
    assert removed_item is not None
    assert removed_item.name == "Test Sword"
    assert len(player.inventory) == 1
    
    # Test level requirement
    high_level_item = Item("High Level Item", "Requires level 10", "weapon", "rare", 10, {"damage": 10.0})
    assert not player.add_item(high_level_item)

def test_player_equipment(player):
    """Test equipment system."""
    # Create test items
    sword = Item("Test Sword", "A test weapon", "weapon", "common", 1, {"damage": 5.0})
    shield = Item("Test Shield", "A test armor", "armor", "common", 1, {"defense": 3.0})
    
    # Add items to inventory
    player.add_item(sword)
    player.add_item(shield)
    
    # Test equipping items
    assert player.equip_item("Test Sword")
    assert player.equip_item("Test Shield")
    assert len(player.equipped_items) == 2
    
    # Test stat application
    assert player.stats.damage == 15.0  # Base 10 + 5 from sword
    assert player.stats.defense == 8.0  # Base 5 + 3 from shield
    
    # Test unequipping
    unequipped = player.unequip_item("weapon")
    assert unequipped is not None
    assert unequipped.name == "Test Sword"
    assert player.stats.damage == 10.0  # Back to base damage

def test_player_input_handling(player):
    """Test input handling."""
    # Test movement input
    keys = defaultdict(int, {pygame.K_w: 1, pygame.K_s: 0, pygame.K_a: 0, pygame.K_d: 1})
    mouse_pos = (100, 100)
    mouse_buttons = (0, 0, 0)
    
    player.handle_input(keys, mouse_pos, mouse_buttons)
    assert pytest.approx(player.move_direction.x, 0.01) == 0.7071  # Diagonal right
    assert pytest.approx(player.move_direction.y, 0.01) == -0.7071  # Diagonal up
    
    # Test shooting input
    mouse_buttons = (1, 0, 0)  # Left mouse button
    player.handle_input(keys, mouse_pos, mouse_buttons)
    assert player.is_shooting
    # shoot_direction may still be zero if transform.x == mouse_x and transform.y == mouse_y
    # so we set a different mouse_pos
    mouse_pos = (200, 200)
    player.handle_input(keys, mouse_pos, mouse_buttons)
    assert player.shoot_direction.length() > 0

def test_player_shooting(player):
    """Test shooting mechanics."""
    # Set up shooting direction
    player.shoot_direction = Vector2(1, 0)  # Shoot right
    player.is_shooting = True
    
    # Mock game world
    class MockGameWorld:
        def __init__(self):
            self.entities = []
        def add_entity(self, entity):
            self.entities.append(entity)
    
    player.game_world = MockGameWorld()
    
    # Test shooting
    player._shoot()
    assert len(player.game_world.entities) == 1
    bullet = player.game_world.entities[0]
    assert isinstance(bullet, Bullet)
    assert bullet.damage == player.stats.damage

def test_player_save_load(player):
    """Test save and load functionality."""
    # Modify player data
    player.stats.level = 5
    player.stats.experience = 200.0
    player.stats.skill_points = 2
    
    # Save data
    player._save_player_data()
    
    # Create new player instance
    new_player = Player(100, 100)
    
    # Verify loaded data
    assert new_player.stats.level == 5
    assert new_player.stats.experience == 200.0
    assert new_player.stats.skill_points == 2

def test_player_abilities_usage(player):
    """Test ability usage."""
    # Test dash ability
    player.move_direction = Vector2(1, 0)  # Moving right
    player._use_dash()
    assert player.abilities.is_dashing
    assert player.abilities.dash_cooldown > 0
    
    # Test ultimate ability
    player._use_ultimate()
    assert player.abilities.is_ultimate_active
    assert player.abilities.ultimate_cooldown > 0
    
    # Test invincibility from ultimate
    health = player.get_component(HealthComponent)
    assert health.is_invincible
    assert health.invincibility_time > 0

def test_player_stat_upgrades(player):
    """Test stat upgrade system."""
    # Remove player data file for a clean state
    try:
        os.remove("data/player_data.json")
    except FileNotFoundError:
        pass
    # Create a new player to ensure clean stats
    player = Player(100, 100)
    # Gain enough experience to level up
    player.gain_experience(100.0)
    assert player.stats.level == 2
    assert player.stats.skill_points == 1
    
    # Test upgrading stats
    initial_health = player.stats.max_health
    initial_speed = player.stats.move_speed
    
    assert player.stats.upgrade_stat("health")
    assert player.stats.max_health > initial_health
    assert player.stats.skill_points == 0
    
    # Test upgrading without skill points
    assert not player.stats.upgrade_stat("speed")
    assert player.stats.move_speed == initial_speed 