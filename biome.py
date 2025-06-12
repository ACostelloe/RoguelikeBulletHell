"""
Biome definitions and management system.
"""
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from logger import logger

@dataclass
class BiomeProperties:
    """Properties for a specific biome."""
    name: str
    tint_color: Tuple[int, int, int]
    tint_strength: float
    overlay_type: Optional[str]
    ambient_particles: str
    music_theme: str
    loot_table: Dict[str, float]  # item_name: weight
    enemy_types: List[str]
    platform_types: List[str]
    hazard_types: List[str]
    background_color: Tuple[int, int, int]
    fog_color: Tuple[int, int, int]
    fog_density: float

class BiomeManager:
    """Manages biome definitions and provides access to biome properties."""
    
    def __init__(self):
        self.biomes: Dict[str, BiomeProperties] = {}
        self._initialize_biomes()
        logger.info("Biome manager initialized")
    
    def _initialize_biomes(self):
        """Initialize all biome definitions."""
        # Grass biome
        self.biomes['grass'] = BiomeProperties(
            name='grass',
            tint_color=(144, 238, 144),
            tint_strength=0.2,
            overlay_type=None,
            ambient_particles='leaves',
            music_theme='forest',
            loot_table={
                'health_potion': 0.3,
                'speed_boost': 0.2,
                'shield': 0.1
            },
            enemy_types=['slime', 'flying_eye'],
            platform_types=['normal', 'bouncy'],
            hazard_types=['spikes'],
            background_color=(200, 255, 200),
            fog_color=(150, 255, 150),
            fog_density=0.1
        )
        
        # Lava biome
        self.biomes['lava'] = BiomeProperties(
            name='lava',
            tint_color=(255, 69, 0),
            tint_strength=0.4,
            overlay_type='cracks',
            ambient_particles='embers',
            music_theme='volcanic',
            loot_table={
                'fire_resistance': 0.4,
                'damage_boost': 0.3,
                'explosive_ammo': 0.2
            },
            enemy_types=['fire_elemental', 'lava_slime'],
            platform_types=['damaging', 'moving'],
            hazard_types=['lava_pool', 'fire_trap'],
            background_color=(255, 100, 0),
            fog_color=(255, 50, 0),
            fog_density=0.3
        )
        
        # Tech biome
        self.biomes['tech'] = BiomeProperties(
            name='tech',
            tint_color=(70, 130, 180),
            tint_strength=0.4,
            overlay_type='glow',
            ambient_particles='sparks',
            music_theme='electronic',
            loot_table={
                'energy_shield': 0.3,
                'laser_weapon': 0.2,
                'teleport': 0.1
            },
            enemy_types=['robot', 'turret'],
            platform_types=['moving', 'grapple_boost'],
            hazard_types=['laser', 'electric_field'],
            background_color=(50, 50, 100),
            fog_color=(100, 100, 255),
            fog_density=0.2
        )
        
        # Ice biome
        self.biomes['ice'] = BiomeProperties(
            name='ice',
            tint_color=(173, 216, 230),
            tint_strength=0.4,
            overlay_type='frost',
            ambient_particles='snow',
            music_theme='arctic',
            loot_table={
                'ice_shield': 0.3,
                'freeze_weapon': 0.2,
                'speed_boost': 0.1
            },
            enemy_types=['ice_golem', 'frost_wisp'],
            platform_types=['slippery', 'breakable'],
            hazard_types=['ice_spike', 'snowstorm'],
            background_color=(200, 230, 255),
            fog_color=(200, 255, 255),
            fog_density=0.4
        )
        
        # Forest biome
        self.biomes['forest'] = BiomeProperties(
            name='forest',
            tint_color=(0, 100, 0),
            tint_strength=0.3,
            overlay_type=None,
            ambient_particles='leaves',
            music_theme='forest',
            loot_table={
                'healing_herb': 0.4,
                'nature_weapon': 0.2,
                'stealth_cloak': 0.1
            },
            enemy_types=['forest_spirit', 'poison_plant'],
            platform_types=['normal', 'bouncy'],
            hazard_types=['poison_mist', 'thorn_trap'],
            background_color=(50, 150, 50),
            fog_color=(100, 200, 100),
            fog_density=0.2
        )
    
    def get_biome(self, name: str) -> Optional[BiomeProperties]:
        """Get biome properties by name."""
        return self.biomes.get(name)
    
    def get_biome_tint(self, name: str) -> Tuple[Tuple[int, int, int], float]:
        """Get biome tint color and strength."""
        biome = self.get_biome(name)
        if biome:
            return biome.tint_color, biome.tint_strength
        return (255, 255, 255), 0.0
    
    def get_biome_overlay(self, name: str) -> Optional[str]:
        """Get biome overlay type."""
        biome = self.get_biome(name)
        return biome.overlay_type if biome else None
    
    def get_biome_loot_table(self, name: str) -> Dict[str, float]:
        """Get biome loot table."""
        biome = self.get_biome(name)
        return biome.loot_table if biome else {}
    
    def get_biome_enemies(self, name: str) -> List[str]:
        """Get biome enemy types."""
        biome = self.get_biome(name)
        return biome.enemy_types if biome else []
    
    def get_biome_platforms(self, name: str) -> List[str]:
        """Get biome platform types."""
        biome = self.get_biome(name)
        return biome.platform_types if biome else []
    
    def get_biome_hazards(self, name: str) -> List[str]:
        """Get biome hazard types."""
        biome = self.get_biome(name)
        return biome.hazard_types if biome else []
    
    def get_biome_ambient(self, name: str) -> Tuple[str, str]:
        """Get biome ambient particles and music theme."""
        biome = self.get_biome(name)
        if biome:
            return biome.ambient_particles, biome.music_theme
        return 'none', 'none'
    
    def get_biome_visuals(self, name: str) -> Tuple[Tuple[int, int, int], Tuple[int, int, int], float]:
        """Get biome background color, fog color, and fog density."""
        biome = self.get_biome(name)
        if biome:
            return biome.background_color, biome.fog_color, biome.fog_density
        return (0, 0, 0), (0, 0, 0), 0.0

# Create global instance
biome_manager = BiomeManager() 