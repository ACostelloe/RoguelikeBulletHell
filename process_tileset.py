import pygame
import os
from PIL import Image

def process_tileset():
    # Initialize pygame
    pygame.init()
    
    # Create directories if they don't exist
    if not os.path.exists('assets/platform_tiles'):
        os.makedirs('assets/platform_tiles')
    
    # Load the tileset sheet
    tileset_path = 'assets/RetroPlatformerTilesets/Tilesets_Sheet.png'
    tileset = pygame.image.load(tileset_path)
    
    # Define tile size (32x32 pixels)
    TILE_SIZE = 32
    
    # Define platform tile positions in the sheet
    # These are the positions of platform tiles in the sheet
    platform_tiles = {
        'left': (0, 0),      # Left edge tile
        'middle': (1, 0),    # Middle tile
        'right': (2, 0),     # Right edge tile
        'single': (3, 0),    # Single tile platform
        'left_damaged': (0, 1),  # Damaged left edge
        'middle_damaged': (1, 1), # Damaged middle
        'right_damaged': (2, 1),  # Damaged right edge
        'left_ice': (0, 2),      # Ice left edge
        'middle_ice': (1, 2),    # Ice middle
        'right_ice': (2, 2),     # Ice right edge
        'left_grass': (0, 3),    # Grass left edge
        'middle_grass': (1, 3),  # Grass middle
        'right_grass': (2, 3),   # Grass right edge
    }
    
    # Extract and save each tile
    for tile_name, (x, y) in platform_tiles.items():
        # Calculate the position in the sheet
        pos_x = x * TILE_SIZE
        pos_y = y * TILE_SIZE
        
        # Extract the tile
        tile_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        tile_surface.blit(tileset, (0, 0), (pos_x, pos_y, TILE_SIZE, TILE_SIZE))
        
        # Save the tile
        pygame.image.save(tile_surface, f'assets/platform_tiles/{tile_name}.png')
    
    print("Tileset processing complete!")

if __name__ == "__main__":
    process_tileset() 