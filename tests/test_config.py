"""
Test configuration and utilities for the bullet hell game.
"""
import os
import sys
import pygame
from typing import Dict, Any

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test parameters
TEST_PARAMS = {
    'screen_width': 800,
    'screen_height': 600,
    'fps': 60,
    'test_duration': 5,  # seconds
    'biome_test_iterations': 100,
    'loot_test_iterations': 1000,
    'music_test_duration': 3,  # seconds
}

# Test biome configurations
TEST_BIOMES = {
    'grass': {
        'tint_color': (144, 238, 144),
        'tint_strength': 0.2,
        'overlay_type': None,
        'ambient_particles': 'leaves',
        'music_theme': 'forest',
        'loot_table': {
            'health_potion': 0.3,
            'speed_boost': 0.2,
            'shield': 0.1
        }
    },
    'lava': {
        'tint_color': (255, 69, 0),
        'tint_strength': 0.4,
        'overlay_type': 'cracks',
        'ambient_particles': 'embers',
        'music_theme': 'volcanic',
        'loot_table': {
            'fire_resistance': 0.4,
            'damage_boost': 0.3,
            'explosive_ammo': 0.2
        }
    }
}

# Test biome layouts
TEST_BIOME_LAYOUTS = {
    'grass': {
        'platforms': ['ground', 'floating'],
        'decorations': ['trees', 'bushes', 'flowers'],
        'hazards': ['spikes', 'pits'],
        'enemy_spawns': ['ground', 'air']
    },
    'lava': {
        'platforms': ['magma', 'obsidian'],
        'decorations': ['crystals', 'geysers'],
        'hazards': ['lava_pools', 'fire_traps'],
        'enemy_spawns': ['ground', 'air']
    }
}

# Test biome enemies
TEST_BIOME_ENEMIES = {
    'grass': ['slime', 'goblin'],
    'lava': ['fire_imp', 'magma_beast']
}

# Test biome decorations
TEST_BIOME_DECORATIONS = {
    'grass': ['flowers', 'bushes', 'trees'],
    'lava': ['crystals', 'geysers']
}

# Test loot items
TEST_LOOT_ITEMS = {
    'common': {
        'health_potion': {
            'name': 'Health Potion',
            'rarity': 'common',
            'biome_origin': None,
            'effect': 'healing',
            'description': 'Restores 25 health.',
            'effect_values': {'healing': 25.0},
            'weight': 0.3
        },
        'speed_boost': {
            'name': 'Speed Boost',
            'rarity': 'common',
            'biome_origin': None,
            'effect': None,
            'description': 'Increases speed for a short time.',
            'effect_values': {},
            'weight': 0.2
        }
    },
    'uncommon': {
        'ember_orb': {
            'name': 'Ember Orb',
            'rarity': 'uncommon',
            'biome_origin': 'lava',
            'effect': 'burn',
            'description': 'Applies burn to enemies on hit.',
            'effect_values': {'burn': 10.0},
            'weight': 0.3
        },
        'frost_shard': {
            'name': 'Frost Shard',
            'rarity': 'uncommon',
            'biome_origin': 'ice',
            'effect': 'freeze',
            'description': 'Chance to freeze enemies.',
            'effect_values': {'freeze': 5.0},
            'weight': 0.3
        }
    },
    'rare': {
        'storm_core': {
            'name': 'Storm Core',
            'rarity': 'rare',
            'biome_origin': 'tech',
            'effect': 'chain_lightning',
            'description': 'Chain lightning on hit.',
            'effect_values': {'chain_lightning': 15.0},
            'weight': 0.2
        },
        'nature_blessing': {
            'name': "Nature's Blessing",
            'rarity': 'rare',
            'biome_origin': 'forest',
            'effect': 'healing',
            'description': 'Heals over time.',
            'effect_values': {'healing': 10.0},
            'weight': 0.2
        }
    },
    'legendary': {
        'phoenix_feather': {
            'name': 'Phoenix Feather',
            'rarity': 'legendary',
            'biome_origin': 'lava',
            'effect': 'revive',
            'description': 'Revives the player once upon death.',
            'effect_values': {'revive': 1.0},
            'weight': 0.1
        }
    }
}

# Test loot tables
TEST_LOOT_TABLES = {
    'grass': {
        'common': 0.6,
        'uncommon': 0.3,
        'rare': 0.1,
        'legendary': 0.0
    },
    'lava': {
        'common': 0.4,
        'uncommon': 0.4,
        'rare': 0.15,
        'legendary': 0.05
    }
}

def init_pygame():
    """Initialize Pygame for testing."""
    pygame.init()
    pygame.display.set_mode((TEST_PARAMS['screen_width'], TEST_PARAMS['screen_height']))
    pygame.display.set_caption("Bullet Hell Game Tests")

def cleanup_pygame():
    """Clean up Pygame after testing."""
    pygame.quit()

def assert_biome_properties(biome: Dict[str, Any], expected: Dict[str, Any]):
    """Assert that biome properties match expected values."""
    for key, value in expected.items():
        assert key in biome, f"Missing property: {key}"
        assert biome[key] == value, f"Property {key} mismatch: expected {value}, got {biome[key]}"

def assert_loot_properties(loot: Dict[str, Any], expected: Dict[str, Any]):
    """Assert that loot properties match expected values."""
    for key, value in expected.items():
        assert key in loot, f"Missing property: {key}"
        assert loot[key] == value, f"Property {key} mismatch: expected {value}, got {loot[key]}"

def assert_music_playing(music_manager) -> bool:
    """Assert that music is currently playing."""
    return pygame.mixer.music.get_busy()

def assert_surface_valid(surface: pygame.Surface) -> bool:
    """Assert that a surface is valid and has the expected properties."""
    return (
        surface is not None and
        isinstance(surface, pygame.Surface) and
        surface.get_width() > 0 and
        surface.get_height() > 0
    ) 