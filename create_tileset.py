from PIL import Image, ImageDraw
import os

def create_platform_tileset():
    # Create a new image with a transparent background
    tile_size = 32
    tileset = Image.new('RGBA', (tile_size * 4, tile_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tileset)
    
    # Define colors
    base_color = (100, 100, 100)
    highlight_color = (150, 150, 150)
    shadow_color = (50, 50, 50)
    
    # Draw left tile
    draw.rectangle([0, 0, tile_size, tile_size], fill=base_color)
    draw.rectangle([0, 0, tile_size, tile_size], outline=highlight_color, width=2)
    draw.rectangle([2, 2, tile_size-2, tile_size-2], outline=shadow_color, width=1)
    
    # Draw middle tile
    draw.rectangle([tile_size, 0, tile_size*2, tile_size], fill=base_color)
    draw.rectangle([tile_size, 0, tile_size*2, tile_size], outline=highlight_color, width=2)
    draw.rectangle([tile_size+2, 2, tile_size*2-2, tile_size-2], outline=shadow_color, width=1)
    
    # Draw right tile
    draw.rectangle([tile_size*2, 0, tile_size*3, tile_size], fill=base_color)
    draw.rectangle([tile_size*2, 0, tile_size*3, tile_size], outline=highlight_color, width=2)
    draw.rectangle([tile_size*2+2, 2, tile_size*3-2, tile_size-2], outline=shadow_color, width=1)
    
    # Draw single tile
    draw.rectangle([tile_size*3, 0, tile_size*4, tile_size], fill=base_color)
    draw.rectangle([tile_size*3, 0, tile_size*4, tile_size], outline=highlight_color, width=2)
    draw.rectangle([tile_size*3+2, 2, tile_size*4-2, tile_size-2], outline=shadow_color, width=1)
    
    # Save the tileset
    if not os.path.exists('assets'):
        os.makedirs('assets')
    tileset.save('assets/platforms.png')

if __name__ == '__main__':
    create_platform_tileset() 