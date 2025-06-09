import pygame
import math
import random
from typing import List, Tuple, Optional
from game_platform import Platform
from biome_generator import BiomeGenerator

class LevelGenerator:
    def __init__(self, width: int, height: int, seed: int = None):
        self.width = width
        self.height = height
        self.seed = seed if seed is not None else random.randint(0, 1000000)
        random.seed(self.seed)
        
        # Initialize biome generator
        self.biome_generator = BiomeGenerator(width, height, self.seed)
        
        # Platform settings
        self.platforms = pygame.sprite.Group()
        self.platform_types = ['normal', 'bouncy', 'slippery', 'breakable', 'damaging']
        
        # Generate initial terrain
        self._generate_initial_terrain()

    def _generate_initial_terrain(self):
        """Generate the initial terrain using biome generator."""
        # Generate terrain for the first few chunks
        for x in range(0, min(1000, self.width)):
            platforms = self.biome_generator.generate_terrain(x)
            for platform_data in platforms:
                x, y, width, color, platform_type = platform_data
                platform = Platform(x * 32, y * 32, width * 32, 32)
                platform.platform_type = platform_type
                platform.image.fill(color)
                self.platforms.add(platform)

    def update(self, camera_x: int):
        """Update the level by generating new terrain as the player moves."""
        # Generate new terrain ahead of the camera
        future_x = int(camera_x + 1000)  # Generate 1000 pixels ahead
        if future_x < self.width:
            platforms = self.biome_generator.generate_terrain(future_x)
            for platform_data in platforms:
                x, y, width, color, platform_type = platform_data
                platform = Platform(x * 32, y * 32, width * 32, 32)
                platform.platform_type = platform_type
                platform.image.fill(color)
                self.platforms.add(platform)

    def get_spawn_position(self, platforms) -> Tuple[int, int]:
        """Get a valid spawn position for the player on a random platform."""
        # Filter platforms that are not win platforms and are within the first biome
        valid_platforms = [p for p in platforms if not p.is_win_platform and p.rect.x < 1000]
        
        if valid_platforms:
            # Choose a random platform
            spawn_platform = random.choice(valid_platforms)
            # Spawn on top of the platform, accounting for player height
            spawn_x = spawn_platform.rect.centerx
            spawn_y = spawn_platform.rect.top - 40  # 40 is player height
            return (spawn_x, spawn_y)
        
        # Fallback spawn position
        return (self.width // 2, self.height - 100)

    def get_biome_at(self, x: int) -> str:
        """Get the biome type at a specific x position."""
        return self.biome_generator.get_biome_at(x)

    def get_enemy_types(self, x: int) -> List[str]:
        """Get the enemy types that can spawn at a specific x position."""
        return self.biome_generator.get_enemy_types(x)

    def get_ambient_particles(self, x: int) -> str:
        """Get the ambient particle type for the current biome."""
        return self.biome_generator.get_ambient_particles(x)

    def draw_background(self, screen: pygame.Surface, camera_x: int):
        """Draw the biome background."""
        self.biome_generator.draw_biome_background(screen, camera_x)

    def create_boundary_platforms(self):
        """Create platforms that form a border around the level."""
        border_platforms = []
        
        # Top border
        border_platforms.append(Platform(0, 0, self.width, self.border_width))
        
        # Bottom border
        border_platforms.append(Platform(0, self.height - self.border_width, self.width, self.border_width))
        
        # Left border
        border_platforms.append(Platform(0, 0, self.border_width, self.height))
        
        # Right border
        border_platforms.append(Platform(self.width - self.border_width, 0, self.border_width, self.height))
        
        return border_platforms

    def generate_level(self, level_number):
        """Generate a new level with platforms and a win platform."""
        platforms = []
        
        # Add border platforms
        platforms.extend(self.create_boundary_platforms())
        
        # Generate regular platforms
        current_y = self.height - 100
        for i in range(self.num_platforms):
            # Calculate platform width and position
            platform_width = random.randint(self.min_platform_width, self.max_platform_width)
            platform_height = random.randint(self.min_platform_height, self.max_platform_height)
            
            # Ensure platforms stay within screen bounds, accounting for border width
            min_x = self.border_width
            max_x = self.width - self.border_width - platform_width
            platform_x = random.randint(min_x, max_x)
            
            # Create platform
            platform = Platform(platform_x, current_y, platform_width, platform_height)
            platforms.append(platform)
            
            # Move up for next platform
            current_y -= random.randint(self.min_platform_distance, self.max_platform_distance)
            
            # Stop if we've gone too high
            if current_y < self.border_width + 100:
                break
        
        # Add win platform at the top
        win_x = (self.width - self.win_platform_size) // 2
        win_y = self.border_width + 50  # Place it just above the top border
        win_platform = Platform(win_x, win_y, self.win_platform_size, self.win_platform_size)
        win_platform.is_win_platform = True
        platforms.append(win_platform)
        
        return platforms 