import random
import math
import noise
import pygame
from typing import List, Tuple, Dict

# If Platform is imported, use from game_platform import Platform

# Biome types and their properties
BIOMES = {
    'sand': {
        'color': (194, 178, 128),
        'platform_color': (210, 180, 140),
        'platform_density': 0.3,
        'platform_height': (4, 8),  # Doubled for 32-bit
        'enemy_types': ['crawler', 'burrower'],
        'powerup_chance': 0.1,
        'hazard_chance': 0.2,
        'ambient_particles': 'sand',
        'tile_size': 32  # 32-bit pixel art
    },
    'ice': {
        'color': (200, 232, 241),
        'platform_color': (220, 240, 255),
        'platform_density': 0.4,
        'platform_height': (6, 12),  # Doubled for 32-bit
        'enemy_types': ['slider', 'ice_shooter'],
        'powerup_chance': 0.15,
        'hazard_chance': 0.3,
        'ambient_particles': 'snow',
        'tile_size': 32
    },
    'mountains': {
        'color': (139, 137, 137),
        'platform_color': (169, 169, 169),
        'platform_density': 0.5,
        'platform_height': (8, 16),  # Doubled for 32-bit
        'enemy_types': ['climber', 'rock_thrower'],
        'powerup_chance': 0.2,
        'hazard_chance': 0.4,
        'ambient_particles': 'rock',
        'tile_size': 32
    },
    'open_fields': {
        'color': (144, 238, 144),
        'platform_color': (152, 251, 152),
        'platform_density': 0.25,
        'platform_height': (2, 6),  # Doubled for 32-bit
        'enemy_types': ['flyer', 'charger'],
        'powerup_chance': 0.25,
        'hazard_chance': 0.1,
        'ambient_particles': 'grass',
        'tile_size': 32
    },
    'urban': {
        'color': (128, 128, 128),
        'platform_color': (169, 169, 169),
        'platform_density': 0.6,
        'platform_height': (4, 10),  # Doubled for 32-bit
        'enemy_types': ['turret', 'drone'],
        'powerup_chance': 0.3,
        'hazard_chance': 0.25,
        'ambient_particles': 'debris',
        'tile_size': 32
    }
}

class BiomeGenerator:
    def __init__(self, width: int, height: int, seed: int = None):
        self.width = width
        self.height = height
        self.seed = seed if seed is not None else random.randint(0, 1000000)
        random.seed(self.seed)
        
        # Initialize noise seeds
        self.terrain_noise = noise.pnoise2
        self.biome_noise = noise.pnoise2
        
        # Biome transition settings
        self.biome_scale = 0.01
        self.terrain_scale = 0.05
        self.biome_blend = 0.1
        
        # Generate biome map
        self.biome_map = self._generate_biome_map()
        
        # Store biome-specific data
        self.biome_data = {}
        for biome in BIOMES:
            self.biome_data[biome] = {
                'platforms': [],
                'enemies': [],
                'powerups': [],
                'hazards': []
            }

    def _generate_biome_map(self) -> List[Dict]:
        """Generate a map of biomes with smooth transitions."""
        biome_map = []
        # First pass: assign biome types and strengths
        for x in range(self.width):
            biome_value = self.biome_noise(x * self.biome_scale, self.seed)
            if biome_value < -0.6:
                biome = 'sand'
            elif biome_value < -0.2:
                biome = 'ice'
            elif biome_value < 0.2:
                biome = 'mountains'
            elif biome_value < 0.6:
                biome = 'open_fields'
            else:
                biome = 'urban'
            biome_map.append({
                'type': biome,
                'strength': abs(biome_value),
                'transition': None  # Placeholder for now
            })
        # Second pass: assign transitions
        for x in range(self.width):
            if x == 0 or x == self.width - 1:
                biome_map[x]['transition'] = {'left': None, 'right': None}
            else:
                current_biome = biome_map[x]['type']
                left_biome = biome_map[x-1]['type']
                right_biome = biome_map[x+1]['type']
                biome_map[x]['transition'] = {
                    'left': left_biome if left_biome != current_biome else None,
                    'right': right_biome if right_biome != current_biome else None
                }
        return biome_map

    def generate_terrain(self, x: int) -> List[Tuple[int, int, str]]:
        """Generate terrain features for a specific x position."""
        biome = self.biome_map[x]['type']
        biome_props = BIOMES[biome]
        
        # Generate base terrain height using noise
        base_height = int(self.terrain_noise(x * self.terrain_scale, self.seed) * 20 + self.height * 0.7)  # Doubled noise scale
        
        # Generate platforms
        platforms = []
        platform_count = int(biome_props['platform_density'] * 10)
        
        for _ in range(platform_count):
            platform_height = random.randint(*biome_props['platform_height'])
            platform_y = base_height - random.randint(0, self.height // 2)
            platform_width = random.randint(6, 16)  # Doubled for 32-bit
            
            # Add platform with biome-specific properties
            platforms.append((
                x,
                platform_y,
                platform_width,
                biome_props['platform_color'],
                self._get_platform_type(biome)
            ))
            
        return platforms

    def _get_platform_type(self, biome: str) -> str:
        """Get platform type based on biome and random chance."""
        biome_props = BIOMES[biome]
        
        # Determine platform type based on biome properties
        if random.random() < biome_props['hazard_chance']:
            return 'damaging'
        elif random.random() < biome_props['powerup_chance']:
            return random.choice(['healing', 'shield', 'speed_boost'])
        else:
            return random.choice(['normal', 'bouncy', 'slippery'])

    def get_biome_at(self, x: int) -> str:
        """Get the biome type at a specific x position."""
        x = max(0, min(x, self.width - 1))
        return self.biome_map[x]['type']

    def get_biome_properties(self, x: int) -> Dict:
        """Get the properties of the biome at a specific x position."""
        x = max(0, min(x, self.width - 1))
        biome = self.get_biome_at(x)
        return BIOMES[biome]

    def get_enemy_types(self, x: int) -> List[str]:
        """Get the enemy types that can spawn in the biome at x position."""
        x = max(0, min(x, self.width - 1))
        biome = self.get_biome_at(x)
        return BIOMES[biome]['enemy_types']

    def get_ambient_particles(self, x: int) -> str:
        """Get the ambient particle type for the biome at x position."""
        x = max(0, min(x, self.width - 1))
        biome = self.get_biome_at(x)
        return BIOMES[biome]['ambient_particles']

    def draw_biome_background(self, screen: pygame.Surface, camera_x: int):
        """Draw the biome background with smooth transitions."""
        for x in range(int(camera_x), int(camera_x + screen.get_width())):
            if 0 <= x < self.width:
                biome = self.get_biome_at(x)
                color = BIOMES[biome]['color']
                
                # Draw vertical line of biome color
                pygame.draw.line(screen, color, 
                               (x - camera_x, 0),
                               (x - camera_x, screen.get_height())) 