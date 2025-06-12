"""
Game configuration and constants.
"""
import pygame
from typing import Dict, Tuple, List, Optional, Any, Set
from dataclasses import dataclass, field
import json
import os
from logger import logger
import traceback
from base import Component
from entities import Entity, EntityType

# Display settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Bullet Hell Game"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)

# Player settings
PLAYER_SPEED = 5
PLAYER_JUMP_POWER = 15
PLAYER_GRAVITY = 0.8
PLAYER_MAX_FALL_SPEED = 20
PLAYER_HEALTH = 100
PLAYER_BULLET_DAMAGE = 10
PLAYER_SHOOT_DELAY = 20
PLAYER_INVINCIBILITY_TIME = 60  # frames
PLAYER_GRAPPLE_SPEED = 15
PLAYER_GRAPPLE_RANGE = 300
PLAYER_GRAPPLE_COOLDOWN = 1.0
PLAYER_GRAPPLE_DURATION = 2.0
BULLET_SPEED = 10  # Speed of player bullets
BULLET_DAMAGE = PLAYER_BULLET_DAMAGE  # For compatibility
BULLET_SIZE = 8  # For compatibility with code expecting BULLET_SIZE

# Grappling hook settings
HOOK_SPEED = 3
HOOK_MAX_LENGTH = 300
HOOK_RETRACT_SPEED = 3
HOOK_EXTEND_SPEED = 3
HOOK_GRAPPLE_SIZE = 4
HOOK_RANGE = 300

# Enemy settings
ENEMY_SPAWN_RATE = 0.1  # Enemies per frame
ENEMY_BASE_HEALTH = 50
ENEMY_BASE_DAMAGE = 10
ENEMY_BASE_SPEED = 3
ENEMY_HEALTH = 50
ENEMY_BULLET_DAMAGE = 5
ENEMY_SHOOT_DELAY = 60
ENEMY_SPEED = 3
ENEMY_BULLET_SPEED = 7
ENEMY_BULLET_SIZE = 8

# Platform settings
PLATFORM_POSITIONS: List[Tuple[int, int, int, int]] = [
    (100, 400, 200, 32),
    (400, 300, 200, 32),
    (700, 200, 200, 32),
    (300, 500, 200, 32),
    (600, 400, 200, 32)
]

# UI settings
UI_FONT_SIZE = 24
UI_COLOR = WHITE
UI_BACKGROUND_COLOR = (0, 0, 0, 128)  # Semi-transparent black
UI_PADDING = 10
UI_MARGIN = 5

# Game states
class GameState:
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

# Input mappings
INPUT_MAPPINGS = {
    "left": [pygame.K_a, pygame.K_LEFT],
    "right": [pygame.K_d, pygame.K_RIGHT],
    "jump": [pygame.K_w, pygame.K_UP, pygame.K_SPACE],
    "shoot": [pygame.BUTTON_LEFT],
    "grapple": [pygame.BUTTON_RIGHT],
    "pause": [pygame.K_ESCAPE]
}

# Zone settings
ZONE_SIZE = 320  # 10 tiles * 32 pixels
ZONE_LOAD_DISTANCE = 2  # Number of zones to load in each direction

# Biome settings
BIOME_SETTINGS = {
    "forest": {
        "tile_color": (34, 139, 34),  # Forest green
        "hazard": "thorn_bush",
        "enemy_types": ["forest_drone", "tree_turret"],
        "particle_effects": ["leaves", "pollen"]
    },
    "tech": {
        "tile_color": (70, 130, 180),  # Steel blue
        "hazard": "electric_field",
        "enemy_types": ["tech_drone", "laser_turret"],
        "particle_effects": ["sparks", "energy_particles"]
    },
    "lava": {
        "tile_color": (139, 0, 0),  # Dark red
        "hazard": "lava_pool",
        "enemy_types": ["lava_drone", "flame_turret"],
        "particle_effects": ["embers", "smoke"]
    },
    "ice": {
        "tile_color": (135, 206, 235),  # Sky blue
        "hazard": "ice_spike",
        "enemy_types": ["ice_drone", "frost_turret"],
        "particle_effects": ["snowflakes", "frost_particles"]
    }
}

# Zone template settings
ZONE_TEMPLATES = {
    "platform_sequence": {
        "width": 20,
        "height": 12,
        "tile_variants": {
            "platform": ["platform_left", "platform_middle", "platform_right"],
            "background": ["background_1", "background_2", "background_3"]
        }
    },
    "floating_islands": {
        "width": 20,
        "height": 12,
        "tile_variants": {
            "island": ["island_small", "island_medium", "island_large"],
            "background": ["cloud_1", "cloud_2", "cloud_3"]
        }
    }
}

# Inventory settings
INVENTORY_SLOT_SIZE = 40
INVENTORY_SLOT_PADDING = 5
INVENTORY_ROWS = 3
INVENTORY_COLS = 5
INVENTORY_BACKGROUND_COLOR = (0, 0, 0, 200)
INVENTORY_SLOT_COLOR = (50, 50, 50)
INVENTORY_SLOT_HIGHLIGHT_COLOR = (100, 100, 100)

# Loot settings
LOOT_TYPES = {
    "artifact": {
        "rarity": "rare",
        "value": 1000,
        "effects": ["health_boost", "damage_boost"]
    },
    "scrap": {
        "rarity": "common",
        "value": 10,
        "effects": []
    },
    "energy_cell": {
        "rarity": "uncommon",
        "value": 50,
        "effects": ["energy_boost"]
    }
}

# Particle settings
PARTICLE_SETTINGS = {
    "leaves": {
        "color": (34, 139, 34),
        "size_range": (2, 4),
        "velocity_range": (-1, 1),
        "spawn_rate": 0.1
    },
    "sparks": {
        "color": (255, 215, 0),
        "size_range": (1, 3),
        "velocity_range": (-2, 2),
        "spawn_rate": 0.2
    },
    "embers": {
        "color": (255, 69, 0),
        "size_range": (2, 4),
        "velocity_range": (-1, 1),
        "spawn_rate": 0.15
    },
    "snowflakes": {
        "color": (255, 255, 255),
        "size_range": (1, 3),
        "velocity_range": (-0.5, 0.5),
        "spawn_rate": 0.1
    }
}

@dataclass
class ConfigComponent(Component):
    """Component for handling configuration."""
    config_id: str = ""
    config_type: str = "game"
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "config_id": self.config_id,
            "config_type": self.config_type,
            "data": self.data
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfigComponent':
        """Create component from dictionary."""
        return cls(
            config_id=data["config_id"],
            config_type=data["config_type"],
            data=data["data"]
        )

class ConfigManager:
    """Manages game configuration."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.configs: Dict[str, Entity] = {}
        self.default_config: Dict[str, Any] = {
            "game": {
                "screen_width": 800,
                "screen_height": 600,
                "fps": 60,
                "title": "Bullet Hell Game",
                "fullscreen": False,
                "vsync": True
            },
            "player": {
                "health": 100,
                "speed": 300,
                "attack": 10,
                "defense": 5,
                "experience_rate": 1.0
            },
            "enemy": {
                "spawn_rate": 1.0,
                "health_multiplier": 1.0,
                "damage_multiplier": 1.0,
                "speed_multiplier": 1.0
            },
            "audio": {
                "master_volume": 1.0,
                "music_volume": 0.8,
                "sound_volume": 1.0,
                "mute": False
            },
            "input": {
                "keyboard": {
                    "up": pygame.K_w,
                    "down": pygame.K_s,
                    "left": pygame.K_a,
                    "right": pygame.K_d,
                    "shoot": pygame.K_SPACE,
                    "dash": pygame.K_LSHIFT,
                    "ultimate": pygame.K_q
                },
                "gamepad": {
                    "deadzone": 0.1,
                    "vibration": True
                }
            },
            "graphics": {
                "particle_quality": "high",
                "lighting_quality": "medium",
                "shadow_quality": "low",
                "anti_aliasing": True,
                "bloom": True
            },
            "debug": {
                "show_fps": False,
                "show_hitboxes": False,
                "show_grid": False,
                "god_mode": False
            }
        }
        
    def create_config(self, config_id: str, config_type: str,
                     data: Optional[Dict[str, Any]] = None) -> Entity:
        """Create a new configuration."""
        try:
            # Create entity
            entity = Entity(EntityType.EFFECT)
            
            # Create config component
            config = ConfigComponent(
                config_id=config_id,
                config_type=config_type,
                data=data or {}
            )
            entity.add_component(config)
            
            # Store config
            self.configs[config_id] = entity
            return entity
            
        except Exception as e:
            logger.error(f"Error creating configuration: {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
    def delete_config(self, config_id: str) -> None:
        """Delete a configuration."""
        try:
            if config_id in self.configs:
                del self.configs[config_id]
                
        except Exception as e:
            logger.error(f"Error deleting configuration: {str(e)}")
            logger.error(traceback.format_exc())
            
    def get_config(self, config_id: str) -> Optional[Entity]:
        """Get a configuration by ID."""
        return self.configs.get(config_id)
        
    def get_value(self, config_id: str, key: str,
                  default: Any = None) -> Any:
        """Get a configuration value."""
        try:
            config = self.get_config(config_id)
            if not config:
                return default
                
            config_component = config.get_component(ConfigComponent)
            if not config_component:
                return default
                
            return config_component.data.get(key, default)
            
        except Exception as e:
            logger.error(f"Error getting configuration value: {str(e)}")
            logger.error(traceback.format_exc())
            return default
            
    def set_value(self, config_id: str, key: str, value: Any) -> None:
        """Set a configuration value."""
        try:
            config = self.get_config(config_id)
            if not config:
                return
                
            config_component = config.get_component(ConfigComponent)
            if not config_component:
                return
                
            config_component.data[key] = value
            
        except Exception as e:
            logger.error(f"Error setting configuration value: {str(e)}")
            logger.error(traceback.format_exc())
            
    def load_config(self, filename: str) -> None:
        """Load configuration from file."""
        try:
            if not os.path.exists(filename):
                return
                
            with open(filename, 'r') as f:
                data = json.load(f)
                
            # Create new manager
            new_manager = self.from_dict(data)
            
            # Update current manager
            self.configs = new_manager.configs
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            logger.error(traceback.format_exc())
            
    def save_config(self, filename: str) -> None:
        """Save configuration to file."""
        try:
            data = self.to_dict()
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
                
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            logger.error(traceback.format_exc())
            
    def reset_config(self, config_id: str) -> None:
        """Reset a configuration to default values."""
        try:
            config = self.get_config(config_id)
            if not config:
                return
                
            config_component = config.get_component(ConfigComponent)
            if not config_component:
                return
                
            # Get default values
            default_data = self.default_config.get(config_component.config_type, {})
            
            # Update config
            config_component.data = default_data.copy()
            
        except Exception as e:
            logger.error(f"Error resetting configuration: {str(e)}")
            logger.error(traceback.format_exc())
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert manager to dictionary."""
        return {
            "configs": {
                config_id: entity.get_component(ConfigComponent).to_dict()
                for config_id, entity in self.configs.items()
            }
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfigManager':
        """Create manager from dictionary."""
        manager = cls()
        for config_id, config_data in data["configs"].items():
            entity = Entity(EntityType.EFFECT)
            config = ConfigComponent.from_dict(config_data)
            entity.add_component(config)
            manager.configs[config_id] = entity
        return manager 