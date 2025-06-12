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

def create_overlay_textures():
    """Create overlay textures for platform effects."""
    tile_size = 32
    
    # Create overlays directory if it doesn't exist
    if not os.path.exists('assets/overlays'):
        os.makedirs('assets/overlays')
    
    # Create cracks overlay
    cracks = Image.new('RGBA', (tile_size, tile_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(cracks)
    # Draw random cracks
    for _ in range(5):
        x1 = int(tile_size * 0.2)
        y1 = int(tile_size * 0.2)
        x2 = int(tile_size * 0.8)
        y2 = int(tile_size * 0.8)
        draw.line([(x1, y1), (x2, y2)], fill=(0, 0, 0, 128), width=2)
    cracks.save('assets/overlays/cracks.png')
    
    # Create glow overlay
    glow = Image.new('RGBA', (tile_size, tile_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    # Draw a soft glow effect
    for i in range(10):
        alpha = int(128 * (1 - i/10))
        draw.ellipse([i, i, tile_size-i, tile_size-i], 
                    fill=(255, 255, 255, alpha))
    glow.save('assets/overlays/glow.png')
    
    # Create frost overlay
    frost = Image.new('RGBA', (tile_size, tile_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frost)
    # Draw frost crystals
    for _ in range(8):
        x = int(tile_size * 0.5)
        y = int(tile_size * 0.5)
        size = int(tile_size * 0.2)
        points = [
            (x, y-size),
            (x+size, y),
            (x, y+size),
            (x-size, y)
        ]
        draw.polygon(points, fill=(255, 255, 255, 64))
    frost.save('assets/overlays/frost.png')

if __name__ == '__main__':
    create_platform_tileset()
    create_overlay_textures()
    print("Tileset and overlay creation complete!") 