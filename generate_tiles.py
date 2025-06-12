import pygame
import os

def create_tile(name, color, size=(32, 32)):
    """Create a tile of specified color and save it."""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(color)
    
    # Add a border
    pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 1)
    
    # Save the tile
    os.makedirs(os.path.dirname(name), exist_ok=True)
    pygame.image.save(surface, f"{name}.png")
    print(f"Generated tile: {name}")

def main():
    # Initialize pygame
    pygame.init()
    
    # Create directories
    os.makedirs("assets/platform_tiles", exist_ok=True)
    os.makedirs("assets/lava_tiles", exist_ok=True)
    
    # Platform tiles
    platform_colors = {
        "left": (200, 200, 200),
        "middle": (180, 180, 180),
        "right": (200, 200, 200),
        "single": (190, 190, 190),
        "left_damaged": (150, 150, 150),
        "middle_damaged": (130, 130, 130),
        "right_damaged": (150, 150, 150),
        "left_grass": (100, 200, 100),
        "middle_grass": (80, 180, 80),
        "right_grass": (100, 200, 100),
        "left_ice": (200, 200, 255),
        "middle_ice": (180, 180, 255),
        "right_ice": (200, 200, 255)
    }
    
    # Lava tiles
    lava_colors = {
        "ash": (100, 100, 100),
        "lava": (255, 100, 0),
        "magma": (200, 50, 0),
        "obsidian": (50, 50, 50),
        "left": (255, 150, 0),
        "middle": (255, 100, 0),
        "right": (255, 150, 0),
        "magma_left": (200, 50, 0),
        "magma_middle": (180, 30, 0),
        "magma_right": (200, 50, 0),
        "obsidian_left": (50, 50, 50),
        "obsidian_middle": (40, 40, 40),
        "obsidian_right": (50, 50, 50)
    }
    
    # Generate platform tiles
    for name, color in platform_colors.items():
        create_tile(f"assets/platform_tiles/{name}", color)
    
    # Generate lava tiles
    for name, color in lava_colors.items():
        create_tile(f"assets/lava_tiles/{name}", color)

if __name__ == "__main__":
    main() 