"""
Tile management module.
"""
import pygame
import os
from typing import Tuple, List, Optional, Dict
from config import GREEN
from logger import logger
from visual_effects import apply_tint, apply_overlay
from dataclasses import dataclass
from asset_manager import AssetManager

@dataclass
class Tile:
    """Represents a single tile in the game world."""
    sprite: pygame.Surface
    rect: pygame.Rect
    tile_type: str
    walkable: bool = True
    destructible: bool = False
    health: int = 100

class Platform(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, width: int, height: int, biome_type='grass', overlays=None):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.biome_type = biome_type
        self.overlays = overlays or {}
        logger.debug(f"Created platform at ({x}, {y}) with size {width}x{height}")
        
        # Apply biome-specific effects
        self._apply_biome_effects()

    def _apply_biome_effects(self):
        """Apply biome-specific visual effects to the platform."""
        # Biome-specific tint configurations
        biome_tints = {
            "forest": ((0, 100, 0), 0.3),    # Dark green tint
            "lava": ((255, 69, 0), 0.4),     # Orange-red tint
            "tech": ((70, 130, 180), 0.4),   # Steel blue tint
            "ice": ((173, 216, 230), 0.4),   # Light blue tint
            "grass": ((144, 238, 144), 0.2)  # Light green tint
        }
        
        # Biome-specific overlay configurations
        biome_overlay_types = {
            "forest": None,
            "lava": "cracks",
            "tech": "glow",
            "ice": "frost",
            "grass": None
        }
        
        # Apply tint
        if self.biome_type in biome_tints:
            tint_color, tint_strength = biome_tints[self.biome_type]
            self.image = apply_tint(self.image, tint_color, tint_strength)
        
        # Apply overlay
        overlay_type = biome_overlay_types.get(self.biome_type)
        if overlay_type and overlay_type in self.overlays:
            self.image = apply_overlay(self.image, self.overlays[overlay_type], alpha=150)

class TileFactory:
    """Factory for creating tile instances."""
    
    TILE_SPRITE_MAP = {
        # Platform tiles
        "platform_left": "platform_tiles/left.png",
        "platform_middle": "platform_tiles/middle.png",
        "platform_right": "platform_tiles/right.png",
        "platform_single": "platform_tiles/single.png",
        
        # Damaged platform tiles
        "platform_left_damaged": "platform_tiles/left_damaged.png",
        "platform_middle_damaged": "platform_tiles/middle_damaged.png",
        "platform_right_damaged": "platform_tiles/right_damaged.png",
        
        # Grass platform tiles
        "platform_left_grass": "platform_tiles/left_grass.png",
        "platform_middle_grass": "platform_tiles/middle_grass.png",
        "platform_right_grass": "platform_tiles/right_grass.png",
        
        # Ice platform tiles
        "platform_left_ice": "platform_tiles/left_ice.png",
        "platform_middle_ice": "platform_tiles/middle_ice.png",
        "platform_right_ice": "platform_tiles/right_ice.png",
        
        # Lava tiles
        "ASH_TILE": "lava_tiles/ash.png",
        "LAVA_TILE": "lava_tiles/lava.png",
        "MAGMA_TILE": "lava_tiles/magma.png",
        "OBSIDIAN_TILE": "lava_tiles/obsidian.png",
        
        # Lava platform tiles
        "platform_left_lava": "lava_tiles/left.png",
        "platform_middle_lava": "lava_tiles/middle.png",
        "platform_right_lava": "lava_tiles/right.png",
        
        # Magma platform tiles
        "platform_left_magma": "lava_tiles/magma_left.png",
        "platform_middle_magma": "lava_tiles/magma_middle.png",
        "platform_right_magma": "lava_tiles/magma_right.png",
        
        # Obsidian platform tiles
        "platform_left_obsidian": "lava_tiles/obsidian_left.png",
        "platform_middle_obsidian": "lava_tiles/obsidian_middle.png",
        "platform_right_obsidian": "lava_tiles/obsidian_right.png",
    }
    
    def __init__(self, asset_manager: AssetManager):
        self.asset_manager = asset_manager
        self.tile_sprites: Dict[str, pygame.Surface] = {}
        
    def initialize(self):
        """Initialize tile sprites after video mode is set."""
        self._load_tile_sprites()
        
    def _load_tile_sprites(self):
        """Load all tile sprites."""
        for tile_type, sprite_path in self.TILE_SPRITE_MAP.items():
            try:
                print(f"Trying to load tile sprite: {sprite_path}")
                sprite = self.asset_manager.get_image(sprite_path)
                self.tile_sprites[tile_type] = sprite
            except Exception as e:
                print(f"Failed to load tile sprite: {tile_type} from {sprite_path}")
                logger.warning(f"Unknown tile type: {tile_type}")
                
    def create_tile(self, tile_type: str, x: int, y: int) -> Optional[Tile]:
        """Create a new tile instance."""
        if tile_type not in self.tile_sprites:
            logger.warning(f"Unknown tile type: {tile_type}")
            return None
            
        sprite = self.tile_sprites[tile_type]
        return Tile(tile_type, sprite, x, y)

class TileManager:
    def __init__(self):
        self.tiles: Dict[str, pygame.Surface] = {}
        self.tile_size = 32  # Size of each tile in the tileset
        self.default_tile = pygame.Surface((self.tile_size, self.tile_size))
        self.default_tile.fill((100, 100, 100))  # Gray color
        self.tiles['default'] = self.default_tile
        self.overlays = {}  # Store overlay textures
        logger.info("Tile manager initialized")
        
    def load_overlays(self):
        """Load overlay textures for biome effects."""
        overlay_path = 'assets/overlays'
        if os.path.exists(overlay_path):
            for filename in os.listdir(overlay_path):
                if filename.endswith('.png'):
                    name = os.path.splitext(filename)[0]
                    path = os.path.join(overlay_path, filename)
                    try:
                        self.overlays[name] = pygame.image.load(path).convert_alpha()
                        logger.debug(f"Loaded overlay texture: {name}")
                    except pygame.error as e:
                        logger.error(f"Error loading overlay {name}: {e}")
        
    def _load_tiles(self) -> None:
        """Load tile textures."""
        # For now, we'll just create a simple tile
        tile = pygame.Surface((32, 32))
        tile.fill(GREEN)
        self.tiles['basic'] = tile
        logger.debug("Loaded basic tile texture")
        
    def create_platform(self, x: int, y: int, width: int, height: int, biome_type='grass') -> Platform:
        """Create a platform at the specified position and size."""
        platform = Platform(x, y, width, height, biome_type=biome_type, overlays=self.overlays)
        logger.debug(f"Created platform at ({x}, {y}) with size {width}x{height}")
        return platform
        
    def create_platform_from_tiles(self, x: int, y: int, pattern: List[List[str]], biome_type='grass') -> Platform:
        """Create a platform from a pattern of tiles."""
        if not pattern or not pattern[0]:
            logger.error("Invalid tile pattern")
            return self.create_platform(x, y, 32, 32, biome_type)
            
        # Calculate platform size
        width = len(pattern[0]) * 32
        height = len(pattern) * 32
        
        # Create platform
        platform = Platform(x, y, width, height, biome_type=biome_type, overlays=self.overlays)
        logger.debug(f"Created platform from pattern at ({x}, {y}) with size {width}x{height}")
        return platform
        
    def get_tile(self, tile_name: str) -> Optional[pygame.Surface]:
        """Get a tile texture by name."""
        return self.tiles.get(tile_name)
        
    def add_tile(self, name: str, surface: pygame.Surface) -> None:
        """Add a new tile texture."""
        self.tiles[name] = surface
        logger.debug(f"Added new tile texture: {name}")
        
    def clear_tiles(self) -> None:
        """Clear all tile textures."""
        self.tiles.clear()
        logger.debug("Cleared all tile textures")
        
    def load_tiles(self, path):
        """Load and split the tileset into individual tiles."""
        try:
            tileset = pygame.image.load(path).convert_alpha()
            tileset_width = tileset.get_width()
            tileset_height = tileset.get_height()
            tiles_x = tileset_width // self.tile_size
            tiles_y = tileset_height // self.tile_size
            for y in range(tiles_y):
                for x in range(tiles_x):
                    tile_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                    tile_surface.blit(tileset, (0, 0), (x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size))
                    tile_key = f"tile_{x}_{y}"
                    self.tiles[tile_key] = tile_surface
            logger.info(f"Loaded {len(self.tiles)} tiles from tileset")
        except Exception as e:
            logger.error(f"Error loading tileset: {e}")
            self.tiles['default'] = self.default_tile
    
    def create_platform_group(self, x, y, width, height, tile_type='platform', biome_type='grass'):
        """Create a platform using tiles from the tileset."""
        platform_group = pygame.sprite.Group()
        tiles_x = width // self.tile_size
        tiles_y = height // self.tile_size
        
        # Use a simple grass platform: left, middle, right (top row)
        left_tile = self.tiles.get('tile_0_0', self.default_tile)
        mid_tile = self.tiles.get('tile_1_0', self.default_tile)
        right_tile = self.tiles.get('tile_2_0', self.default_tile)
        
        for tx in range(tiles_x):
            if tx == 0:
                tile_img = left_tile
            elif tx == tiles_x - 1:
                tile_img = right_tile
            else:
                tile_img = mid_tile
            
            tile = Tile(x + tx * self.tile_size, y, tile_img, tile_type, biome_type, self.overlays)
            platform_group.add(tile)
        
        # Optionally add more rows for thicker platforms
        return platform_group
    
    def create_platform_from_tiles_group(self, x, y, tile_pattern, biome_type='grass'):
        """Create a platform using a specific pattern of tiles."""
        platform_group = pygame.sprite.Group()
        
        for row_idx, row in enumerate(tile_pattern):
            for col_idx, tile_key in enumerate(row):
                if tile_key in self.tiles:
                    tile = Tile(
                        x + col_idx * self.tile_size,
                        y + row_idx * self.tile_size,
                        self.tiles[tile_key],
                        'platform',
                        biome_type,
                        self.overlays
                    )
                    platform_group.add(tile)
        
        return platform_group 