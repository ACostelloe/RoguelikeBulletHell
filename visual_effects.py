import pygame
import os
import random
import math

class TilesetManager:
    def __init__(self):
        self.tilesets = {}
        self.tile_mappings = {}

    def load_tileset(self, name, path, tile_width, tile_height):
        """Load a tileset from a directory of individual tile files."""
        self.tilesets[name] = {}
        
        # If path is a directory, load all PNG files in it
        if os.path.isdir(path):
            for filename in os.listdir(path):
                if filename.endswith('.png'):
                    tile_name = os.path.splitext(filename)[0]
                    tile_path = os.path.join(path, filename)
                    try:
                        tile_surface = pygame.image.load(tile_path).convert_alpha()
                        self.tilesets[name][tile_name] = tile_surface
                    except pygame.error as e:
                        print(f"Error loading tile {tile_name}: {e}")
        else:
            # If path is a single file, load it as a tileset sheet
            try:
                tileset_surface = pygame.image.load(path).convert_alpha()
                self.tilesets[name]['sheet'] = tileset_surface
            except pygame.error as e:
                print(f"Error loading tileset {name}: {e}")

    def create_tile_mapping(self, name, mapping):
        """Create a mapping of tile names to their positions in the tileset."""
        self.tile_mappings[name] = mapping

    def get_tile(self, tileset_name, tile_name):
        """Get a tile from the tileset by name."""
        if tileset_name in self.tilesets:
            if tile_name in self.tilesets[tileset_name]:
                return self.tilesets[tileset_name][tile_name]
            elif 'sheet' in self.tilesets[tileset_name] and tileset_name in self.tile_mappings:
                # If using a tileset sheet, calculate position from mapping
                if tile_name in self.tile_mappings[tileset_name]:
                    pos = self.tile_mappings[tileset_name][tile_name]
                    if isinstance(pos, tuple):
                        x, y = pos
                        tile_width = 32  # Assuming 32x32 tiles
                        tile_height = 32
                        return self.tilesets[tileset_name]['sheet'].subsurface(
                            (x * tile_width, y * tile_height, tile_width, tile_height))
        return None

# Create global instance
tileset_manager = TilesetManager()

class VisualEffects:
    @staticmethod
    def apply_glow(surface, color, intensity):
        """Apply a glow effect to a surface."""
        glow = surface.copy()
        glow.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
        glow.set_alpha(intensity)
        return glow

    @staticmethod
    def apply_distortion(surface, amount):
        """Apply a distortion effect to a surface."""
        width, height = surface.get_size()
        distorted = pygame.Surface((width, height), pygame.SRCALPHA)
        
        for x in range(0, width, 2):
            for y in range(0, height, 2):
                offset_x = random.randint(-int(amount * 10), int(amount * 10))
                offset_y = random.randint(-int(amount * 10), int(amount * 10))
                src_x = max(0, min(x + offset_x, width - 1))
                src_y = max(0, min(y + offset_y, height - 1))
                color = surface.get_at((src_x, src_y))
                distorted.set_at((x, y), color)
        
        return distorted

    @staticmethod
    def apply_noise(surface, amount):
        """Apply noise to a surface."""
        width, height = surface.get_size()
        noisy = surface.copy()
        
        for x in range(width):
            for y in range(height):
                if random.random() < amount:
                    color = surface.get_at((x, y))
                    noise = random.randint(-20, 20)
                    new_color = (
                        max(0, min(255, color[0] + noise)),
                        max(0, min(255, color[1] + noise)),
                        max(0, min(255, color[2] + noise)),
                        color[3]
                    )
                    noisy.set_at((x, y), new_color)
        
        return noisy

# Create global instance
visual_effects = VisualEffects()

class BiomeVisuals:
    def __init__(self):
        self.biome_colors = {
            'sand': {
                'base': (194, 178, 128),
                'highlight': (210, 180, 140),
                'shadow': (139, 121, 94)
            },
            'ice': {
                'base': (200, 232, 241),
                'highlight': (220, 240, 255),
                'shadow': (180, 200, 220)
            },
            'grass': {
                'base': (144, 238, 144),
                'highlight': (152, 251, 152),
                'shadow': (124, 205, 124)
            }
        }

    def get_biome_colors(self, biome_type):
        """Get the color scheme for a biome."""
        return self.biome_colors.get(biome_type, self.biome_colors['sand'])

    def apply_biome_colors(self, surface, biome_type):
        """Apply biome-specific colors to a surface."""
        colors = self.get_biome_colors(biome_type)
        colored = surface.copy()
        
        # Create a color overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((*colors['base'], 128))
        
        # Blend the overlay with the original surface
        colored.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        return colored

# Create global instance
biome_visuals = BiomeVisuals() 