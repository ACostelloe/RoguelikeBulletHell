import pygame
import os

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image, tile_type='platform'):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = tile_type

class TileManager:
    def __init__(self):
        self.tiles = {}
        self.tile_size = 32  # Size of each tile in the tileset
        # Create default tile
        self.default_tile = pygame.Surface((self.tile_size, self.tile_size))
        self.default_tile.fill((100, 100, 100))  # Gray color
        self.tiles['default'] = self.default_tile
        self.load_tileset()
        
    def load_tileset(self):
        """Load and split the tileset into individual tiles."""
        try:
            # Load the tileset image
            tileset_path = os.path.join('assets', 'RetroPlatformerTilesets', 'Tilesets_Sheet.png')
            tileset = pygame.image.load(tileset_path).convert_alpha()
            
            # Calculate number of tiles in the tileset
            tileset_width = tileset.get_width()
            tileset_height = tileset.get_height()
            tiles_x = tileset_width // self.tile_size
            tiles_y = tileset_height // self.tile_size
            
            # Split tileset into individual tiles
            for y in range(tiles_y):
                for x in range(tiles_x):
                    # Create a surface for the tile
                    tile_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                    # Copy the tile from the tileset
                    tile_surface.blit(tileset, (0, 0), 
                                    (x * self.tile_size, y * self.tile_size, 
                                     self.tile_size, self.tile_size))
                    
                    # Store the tile with a unique key
                    tile_key = f"tile_{x}_{y}"
                    self.tiles[tile_key] = tile_surface
            
            print(f"Loaded {len(self.tiles)} tiles from tileset")
            
        except Exception as e:
            print(f"Error loading tileset: {e}")
            # Use the default tile if loading fails
            self.tiles['default'] = self.default_tile
    
    def create_platform(self, x, y, width, height, tile_type='platform'):
        """Create a platform using tiles."""
        platform_group = pygame.sprite.Group()
        
        # Calculate number of tiles needed
        tiles_x = width // self.tile_size
        tiles_y = height // self.tile_size
        
        # Select appropriate tiles for the platform
        # For now, using a simple pattern - can be made more complex later
        tile_keys = ['tile_0_0', 'tile_1_0', 'tile_2_0']  # Example tile keys
        
        for ty in range(tiles_y):
            for tx in range(tiles_x):
                # Select tile based on position
                if ty == 0:  # Top row
                    tile_key = tile_keys[1] if 0 < tx < tiles_x - 1 else tile_keys[0]
                elif ty == tiles_y - 1:  # Bottom row
                    tile_key = 'tile_0_2'  # Bottom tile
                else:  # Middle rows
                    tile_key = 'tile_0_1'  # Middle tile
                
                # Create the tile
                tile = Tile(
                    x + tx * self.tile_size,
                    y + ty * self.tile_size,
                    self.tiles.get(tile_key, self.tiles['default']),
                    tile_type
                )
                platform_group.add(tile)
        
        return platform_group
    
    def create_platform_from_tiles(self, x, y, tile_pattern):
        """Create a platform using a specific pattern of tiles."""
        platform_group = pygame.sprite.Group()
        
        for row_idx, row in enumerate(tile_pattern):
            for col_idx, tile_key in enumerate(row):
                if tile_key in self.tiles:
                    tile = Tile(
                        x + col_idx * self.tile_size,
                        y + row_idx * self.tile_size,
                        self.tiles[tile_key],
                        'platform'
                    )
                    platform_group.add(tile)
        
        return platform_group 