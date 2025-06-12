import random
import math
import noise
import pygame
from typing import List, Tuple, Dict, Optional, Any
from noise import pnoise1
from particle_system import ParticleSystem
from dataclasses import dataclass
from zone_types import BiomeType
import json
from logger import logger
import traceback
import logging
import numpy as np

# If Platform is imported, use from game_platform import Platform

class BiomeProperties:
    def __init__(self, name: str, tile_color: Tuple[int, int, int], hazard: str, 
                 enemy_types: List[str], ambient_color: Tuple[int, int, int],
                 platform_variants: List[str], particle_effects: List[str]):
        self.name = name
        self.tile_color = tile_color
        self.hazard = hazard
        self.enemy_types = enemy_types
        self.ambient_color = ambient_color
        self.platform_variants = platform_variants
        self.particle_effects = particle_effects

# Biome definitions with enhanced properties
BIOMES = {
    "forest": BiomeProperties(
        name="forest",
        tile_color=(34, 139, 34),
        hazard="spikes",
        enemy_types=["goblin", "wolf"],
        ambient_color=(100, 150, 100),
        platform_variants=["grass", "moss", "wood"],
        particle_effects=["leaves", "pollen", "fireflies"]
    ),
    "lava": BiomeProperties(
        name="lava",
        tile_color=(255, 69, 0),
        hazard="lava",
        enemy_types=["fire_imp", "magma_beast"],
        ambient_color=(150, 50, 50),
        platform_variants=["magma", "obsidian", "ash"],
        particle_effects=["embers", "smoke", "magma_bubbles"]
    ),
    "tech": BiomeProperties(
        name="tech",
        tile_color=(70, 130, 180),
        hazard="laser",
        enemy_types=["drone", "android"],
        ambient_color=(50, 50, 100),
        platform_variants=["metal", "circuit", "energy"],
        particle_effects=["sparks", "energy_particles", "holograms"]
    ),
    "ice": BiomeProperties(
        name="ice",
        tile_color=(173, 216, 230),
        hazard="slippery",
        enemy_types=["frostling", "yetibot"],
        ambient_color=(200, 230, 255),
        platform_variants=["ice", "snow", "crystal"],
        particle_effects=["snowflakes", "frost", "aurora"]
    ),
}

class BiomeTransition:
    def __init__(self, start_biome: str, end_biome: str, transition_width: int):
        self.start_biome = start_biome
        self.end_biome = end_biome
        self.transition_width = transition_width
        self.progress = 0.0

    def update(self, x: int, start_x: int) -> float:
        self.progress = min(1.0, max(0.0, (x - start_x) / self.transition_width))
        return self.progress

def get_biome_for_chunk(chunk_index, seed=42):
    scale = 0.1
    noise_value = pnoise1(chunk_index * scale, repeat=999999, base=seed)
    thresholds = [(-0.25, "forest"), (0.0, "lava"), (0.25, "tech"), (1.0, "ice")]
    for threshold, biome in thresholds:
        if noise_value <= threshold:
            return biome
    return "forest"

@dataclass
class BiomeSettings:
    """Settings for biome generation."""
    scale: float
    octaves: int
    persistence: float
    lacunarity: float
    seed: int
    threshold: float
    transition_smoothness: float = 0.1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "scale": self.scale,
            "octaves": self.octaves,
            "persistence": self.persistence,
            "lacunarity": self.lacunarity,
            "seed": self.seed,
            "threshold": self.threshold,
            "transition_smoothness": self.transition_smoothness
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BiomeSettings':
        """Create settings from dictionary."""
        return cls(
            scale=data["scale"],
            octaves=data["octaves"],
            persistence=data["persistence"],
            lacunarity=data["lacunarity"],
            seed=data["seed"],
            threshold=data["threshold"],
            transition_smoothness=data.get("transition_smoothness", 0.1)
        )

class BiomeGenerator:
    """Generates biomes using Perlin noise."""
    
    DEFAULT_SETTINGS = {
        BiomeType.FOREST: BiomeSettings(
            scale=50.0,
            octaves=6,
            persistence=0.5,
            lacunarity=2.0,
            seed=random.randint(0, 1000),
            threshold=0.3
        ),
        BiomeType.DESERT: BiomeSettings(
            scale=40.0,
            octaves=4,
            persistence=0.4,
            lacunarity=2.2,
            seed=random.randint(0, 1000),
            threshold=0.4
        ),
        BiomeType.SNOW: BiomeSettings(
            scale=60.0,
            octaves=5,
            persistence=0.6,
            lacunarity=1.8,
            seed=random.randint(0, 1000),
            threshold=0.35
        ),
        BiomeType.VOLCANO: BiomeSettings(
            scale=30.0,
            octaves=3,
            persistence=0.7,
            lacunarity=2.5,
            seed=random.randint(0, 1000),
            threshold=0.45
        ),
        BiomeType.CAVE: BiomeSettings(
            scale=25.0,
            octaves=4,
            persistence=0.5,
            lacunarity=2.3,
            seed=random.randint(0, 1000),
            threshold=0.4
        ),
        BiomeType.CRYSTAL: BiomeSettings(
            scale=45.0,
            octaves=5,
            persistence=0.6,
            lacunarity=2.1,
            seed=random.randint(0, 1000),
            threshold=0.35
        ),
        BiomeType.CORRUPTED: BiomeSettings(
            scale=35.0,
            octaves=4,
            persistence=0.7,
            lacunarity=2.4,
            seed=random.randint(0, 1000),
            threshold=0.4
        ),
        BiomeType.HEAVENLY: BiomeSettings(
            scale=55.0,
            octaves=6,
            persistence=0.5,
            lacunarity=1.9,
            seed=random.randint(0, 1000),
            threshold=0.3
        )
    }
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the biome generator."""
        self.seed = seed if seed is not None else random.randint(0, 1000)
        self.settings = self.DEFAULT_SETTINGS.copy()
        self._initialize_noise()
        
    def _initialize_noise(self) -> None:
        """Initialize noise settings for each biome."""
        for biome_type, settings in self.settings.items():
            settings.seed = (self.seed + hash(biome_type.name)) % 1000
            
    def get_biome_at(self, x: float, y: float = 0.0) -> BiomeType:
        """Get the biome type at the specified coordinates."""
        try:
            # Get noise values for each biome
            noise_values = {}
            for biome_type, settings in self.settings.items():
                noise_value = noise.pnoise2(
                    x / settings.scale,
                    y / settings.scale,
                    octaves=settings.octaves,
                    persistence=settings.persistence,
                    lacunarity=settings.lacunarity,
                    repeatx=1000,
                    repeaty=1000,
                    base=settings.seed
                )
                noise_values[biome_type] = noise_value
                
            # Find the biome with the highest noise value
            max_biome = max(noise_values.items(), key=lambda x: x[1])
            
            # Check if the noise value is above the threshold
            if max_biome[1] > self.settings[max_biome[0]].threshold:
                biome = max_biome[0]
                logging.info(f'Biome generated: {biome}')
                return biome
            else:
                # If below threshold, return a default biome
                return BiomeType.FOREST
                
        except Exception as e:
            logger.error(f"Error getting biome at ({x}, {y}): {str(e)}")
            logger.error(traceback.format_exc())
            return BiomeType.FOREST
            
    def get_biome_transition(self, x: float, y: float, radius: float = 1.0) -> Dict[BiomeType, float]:
        """Get the transition weights between biomes at the specified coordinates."""
        try:
            # Get noise values for each biome
            noise_values = {}
            for biome_type, settings in self.settings.items():
                noise_value = noise.pnoise2(
                    x / settings.scale,
                    y / settings.scale,
                    octaves=settings.octaves,
                    persistence=settings.persistence,
                    lacunarity=settings.lacunarity,
                    repeatx=1000,
                    repeaty=1000,
                    base=settings.seed
                )
                # Apply threshold and smooth transition
                if noise_value > settings.threshold:
                    noise_value = (noise_value - settings.threshold) / (1 - settings.threshold)
                else:
                    noise_value = 0
                noise_values[biome_type] = noise_value
                
            # Normalize values
            total = sum(noise_values.values())
            if total > 0:
                for biome_type in noise_values:
                    noise_values[biome_type] /= total
                    
            return noise_values
            
        except Exception as e:
            logger.error(f"Error getting biome transition at ({x}, {y}): {str(e)}")
            logger.error(traceback.format_exc())
            return {BiomeType.FOREST: 1.0}
            
    def get_biome_features(self, biome_type: BiomeType, x: float, y: float) -> Dict[str, Any]:
        """Get biome-specific features at the specified coordinates."""
        try:
            settings = self.settings[biome_type]
            
            # Generate feature noise
            feature_noise = noise.pnoise2(
                x / (settings.scale * 0.5),
                y / (settings.scale * 0.5),
                octaves=settings.octaves + 1,
                persistence=settings.persistence * 0.8,
                lacunarity=settings.lacunarity * 1.2,
                repeatx=1000,
                repeaty=1000,
                base=settings.seed + 1000
            )
            
            # Map noise to features based on biome type
            features = {}
            if biome_type == BiomeType.FOREST:
                features["tree_density"] = max(0, min(1, (feature_noise + 1) / 2))
                features["foliage_density"] = max(0, min(1, (feature_noise + 0.5) / 1.5))
            elif biome_type == BiomeType.DESERT:
                features["dune_height"] = max(0, min(1, (feature_noise + 1) / 2))
                features["cactus_density"] = max(0, min(1, (feature_noise + 0.3) / 1.3))
            elif biome_type == BiomeType.SNOW:
                features["snow_depth"] = max(0, min(1, (feature_noise + 1) / 2))
                features["ice_formation"] = max(0, min(1, (feature_noise + 0.5) / 1.5))
            elif biome_type == BiomeType.VOLCANO:
                features["lava_flow"] = max(0, min(1, (feature_noise + 1) / 2))
                features["ash_density"] = max(0, min(1, (feature_noise + 0.3) / 1.3))
            elif biome_type == BiomeType.CAVE:
                features["stalactite_density"] = max(0, min(1, (feature_noise + 1) / 2))
                features["crystal_formation"] = max(0, min(1, (feature_noise + 0.5) / 1.5))
            elif biome_type == BiomeType.CRYSTAL:
                features["crystal_size"] = max(0, min(1, (feature_noise + 1) / 2))
                features["crystal_density"] = max(0, min(1, (feature_noise + 0.3) / 1.3))
            elif biome_type == BiomeType.CORRUPTED:
                features["corruption_level"] = max(0, min(1, (feature_noise + 1) / 2))
                features["void_presence"] = max(0, min(1, (feature_noise + 0.5) / 1.5))
            elif biome_type == BiomeType.HEAVENLY:
                features["cloud_density"] = max(0, min(1, (feature_noise + 1) / 2))
                features["light_intensity"] = max(0, min(1, (feature_noise + 0.3) / 1.3))
                
            return features
            
        except Exception as e:
            logger.error(f"Error getting biome features for {biome_type} at ({x}, {y}): {str(e)}")
            logger.error(traceback.format_exc())
            return {}
            
    def get_biome_transition_features(self, x: float, y: float) -> Dict[str, Any]:
        """Get features for biome transitions at the specified coordinates."""
        try:
            # Get transition weights
            transitions = self.get_biome_transition(x, y)
            
            # Get features for each biome
            all_features = {}
            for biome_type, weight in transitions.items():
                if weight > 0:
                    features = self.get_biome_features(biome_type, x, y)
                    for feature, value in features.items():
                        if feature not in all_features:
                            all_features[feature] = 0
                        all_features[feature] += value * weight
                        
            return all_features
            
        except Exception as e:
            logger.error(f"Error getting biome transition features at ({x}, {y}): {str(e)}")
            logger.error(traceback.format_exc())
            return {}
            
    def save_settings(self, file_path: str) -> None:
        """Save biome settings to a file."""
        try:
            settings_dict = {
                biome_type.name: settings.to_dict()
                for biome_type, settings in self.settings.items()
            }
            with open(file_path, "w") as f:
                json.dump(settings_dict, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving biome settings to {file_path}: {str(e)}")
            logger.error(traceback.format_exc())
            
    def load_settings(self, file_path: str) -> None:
        """Load biome settings from a file."""
        try:
            with open(file_path, "r") as f:
                settings_dict = json.load(f)
                
            for biome_name, settings_data in settings_dict.items():
                biome_type = BiomeType[biome_name]
                self.settings[biome_type] = BiomeSettings.from_dict(settings_data)
                
            self._initialize_noise()
            
        except Exception as e:
            logger.error(f"Error loading biome settings from {file_path}: {str(e)}")
            logger.error(traceback.format_exc())
            
    def generate_biome_map(self, width: int, height: int, scale: float = 1.0) -> np.ndarray:
        """Generate a 2D array of biome types."""
        try:
            biome_map = np.zeros((height, width), dtype=np.int32)
            
            for y in range(height):
                for x in range(width):
                    world_x = x * scale
                    world_y = y * scale
                    biome = self.get_biome_at(world_x, world_y)
                    biome_map[y, x] = biome.value
                    
            return biome_map
            
        except Exception as e:
            logger.error(f"Error generating biome map: {str(e)}")
            logger.error(traceback.format_exc())
            return np.zeros((height, width), dtype=np.int32)
            
    def generate_feature_map(self, width: int, height: int, scale: float = 1.0) -> Dict[str, np.ndarray]:
        """Generate a dictionary of feature maps."""
        try:
            feature_maps = {}
            
            for y in range(height):
                for x in range(width):
                    world_x = x * scale
                    world_y = y * scale
                    features = self.get_biome_transition_features(world_x, world_y)
                    
                    for feature, value in features.items():
                        if feature not in feature_maps:
                            feature_maps[feature] = np.zeros((height, width))
                        feature_maps[feature][y, x] = value
                        
            return feature_maps
            
        except Exception as e:
            logger.error(f"Error generating feature maps: {str(e)}")
            logger.error(traceback.format_exc())
            return {}

    def generate_terrain(self, x: int) -> List[Tuple[int, int, int, Tuple[int, int, int], str]]:
        biome = self.biome_map[x]['type']
        biome_props = BIOMES[biome]
        platforms = []
        path_length = 12
        min_width = 3
        max_width = 6
        min_gap = 1
        max_gap = 3
        start_x = x
        start_y = (self.height // 32) - 2
        current_x = start_x
        current_y = start_y
        
        for step in range(path_length):
            width = random.randint(min_width, max_width)
            # Select random platform variant
            variant = random.choice(biome_props.platform_variants)
            platforms.append((current_x, current_y, width, biome_props.tile_color, biome, variant))
            
            dx = random.choice([-1, 0, 1])
            current_x = max(0, min(self.width // 32 - width, current_x + dx * random.randint(min_gap, max_gap)))
            current_y -= 2
            
            if current_y < 2:
                break
                
            if random.random() < 0.2:
                branch_width = random.randint(min_width, max_width)
                branch_x = max(0, min(self.width // 32 - branch_width, 
                                    current_x + random.choice([-1, 1]) * random.randint(2, 4)))
                branch_y = current_y + random.randint(1, 2)
                variant = random.choice(biome_props.platform_variants)
                platforms.append((branch_x, branch_y, branch_width, biome_props.tile_color, biome, variant))
                
        return platforms

    def get_biome_properties(self, x: int) -> BiomeProperties:
        """Get the biome properties at the specified x coordinate."""
        biome_type = self.get_biome_at(x)
        return BIOMES.get(biome_type.name.lower(), BIOMES["forest"])

    def get_enemy_types(self, x: int) -> List[str]:
        """Get the enemy types that can spawn in the biome at x position."""
        x = max(0, min(x, self.width - 1))
        biome = self.get_biome_at(x)
        return BIOMES[biome].enemy_types

    def get_ambient_particles(self, x: int) -> List[str]:
        """Get the ambient particle effects for the biome at x position."""
        x = max(0, min(x, self.width - 1))
        biome = self.get_biome_at(x)
        return BIOMES[biome].particle_effects

    def draw_biome_background(self, screen: pygame.Surface, camera_x: int):
        """Draw the biome background with ambient effects."""
        x = int(camera_x)
        biome = self.get_biome_at(x)
        biome_props = BIOMES[biome]
        
        # Draw base background color
        screen.fill(biome_props.ambient_color)
        
        # Emit ambient particles
        for particle_type in biome_props.particle_effects:
            # Emit particles at random positions across the screen
            for _ in range(3):  # Emit multiple particles per frame
                emit_x = camera_x + random.randint(0, screen.get_width())
                emit_y = random.randint(0, screen.get_height())
                particle_system.emit(particle_type, emit_x, emit_y, 1/60)  # Assuming 60 FPS
        
        # Update and draw particles
        particle_system.update(1/60)  # Assuming 60 FPS
        particle_system.draw(screen, camera_x)

def generate_biome(width: int, height: int, scale: float = 1.0) -> np.ndarray:
    generator = BiomeGenerator()
    return generator.generate_biome_map(width, height, scale) 