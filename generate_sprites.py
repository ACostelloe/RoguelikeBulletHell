import pygame
import os

def create_placeholder_sprite(size, color, filename):
    surface = pygame.Surface(size)
    surface.fill(color)
    pygame.image.save(surface, filename)

def main():
    pygame.init()
    
    # Create player sprite
    create_placeholder_sprite(
        (32, 32),
        (0, 255, 0),  # Green
        "assets/images/player/player.png"
    )
    
    # Create enemy sprites
    enemies = {
        "grunt": (24, 24, (255, 0, 0)),    # Red
        "flyer": (20, 20, (0, 0, 255)),    # Blue
        "tank": (40, 40, (128, 0, 0)),     # Dark Red
        "boss": (64, 64, (128, 0, 128))    # Purple
    }
    
    for name, (width, height, color) in enemies.items():
        create_placeholder_sprite(
            (width, height),
            color,
            f"assets/images/enemies/{name}.png"
        )
    
    pygame.quit()

if __name__ == "__main__":
    main() 