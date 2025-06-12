"""
Zone Template module.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import random
from zone_types import ZoneTile, ZoneDecoration, ZoneEnemy, ZoneLoot, ZoneTransition

@dataclass
class ZoneTemplate:
    name: str
    biome: str
    width: int
    height: int
    tiles: List[ZoneTile]
    decorations: List[ZoneDecoration] = field(default_factory=list)
    enemies: List[ZoneEnemy] = field(default_factory=list)
    loot: List[ZoneLoot] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    spawn_zone: bool = False
    transition_type: Optional[str] = None
    zone_type: Optional[str] = None
    transitions: List[ZoneTransition] = field(default_factory=list)
    
    @staticmethod
    def _create_tile(tile_type: str, x: int, y: int) -> ZoneTile:
        """Create a ZoneTile instance with proper properties."""
        # Define which tile types are platforms
        platform_types = {
            "platform_left", "platform_middle", "platform_right",
            "platform_glow", "platform_tech", "platform_crystal"
        }
        return ZoneTile(type=tile_type, x=x, y=y, is_platform=tile_type in platform_types)
    
    def apply_variations(self, random_seed: Optional[int] = None) -> 'ZoneTemplate':
        """Apply random variations to the zone template."""
        if random_seed is not None:
            random.seed(int(random_seed))  # Convert to int to ensure valid seed type
        
        # Create a copy of the template
        template = ZoneTemplate(
            name=self.name,
            biome=self.biome,
            width=self.width,
            height=self.height,
            tiles=[self._create_tile(tile.type, tile.x, tile.y) for tile in self.tiles],
            decorations=self.decorations.copy(),
            enemies=self.enemies.copy(),
            loot=self.loot.copy(),
            events=self.events.copy(),
            spawn_zone=self.spawn_zone,
            transition_type=self.transition_type,
            zone_type=self.zone_type,
            transitions=self.transitions.copy()
        )
        
        # Apply variations to tiles
        for tile in template.tiles:
            if random.random() < 0.3:  # 30% chance to vary each tile
                tile.variant = self._get_random_variant(tile.type)
        
        # Apply variations to decorations
        for dec in template.decorations:
            if random.random() < 0.2:  # 20% chance to vary each decoration
                dec.properties = self._get_random_decoration_properties(dec.type)
        
        # Apply variations to enemies
        for enemy in template.enemies:
            if random.random() < 0.4:  # 40% chance to add patrol points
                enemy.patrol_points = self._generate_patrol_points(enemy.x, enemy.y)
        
        # Apply variations to loot
        for loot in template.loot:
            if random.random() < 0.3:  # 30% chance to vary loot type
                loot.type = self._get_random_loot_type(loot.rarity)
        
        return template
    
    def _get_random_variant(self, tile_type: str) -> str:
        """Get a random variant for a tile type."""
        variants = {
            "platform_middle": ["normal", "damaged", "reinforced"],
            "platform_glow": ["blue", "green", "red"],
            "tech_tower": ["active", "inactive", "overloaded"]
        }
        return random.choice(variants.get(tile_type, ["normal"]))
    
    def _get_random_decoration_properties(self, dec_type: str) -> Dict:
        """Get random properties for a decoration."""
        properties = {
            "glow_node": {
                "intensity": random.uniform(0.5, 1.0),
                "color": random.choice(["blue", "green", "red"])
            },
            "cable_bundle": {
                "damage": random.uniform(0.0, 0.3),
                "sparks": random.random() < 0.2
            }
        }
        return properties.get(dec_type, {})
    
    def _generate_patrol_points(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Generate patrol points for an enemy."""
        points = []
        num_points = random.randint(2, 4)
        
        for _ in range(num_points):
            dx = random.randint(-3, 3)
            dy = random.randint(-2, 2)
            points.append((x + dx, y + dy))
        
        return points
    
    def _get_random_loot_type(self, rarity: str) -> str:
        """Get a random loot type based on rarity."""
        loot_types = {
            "common": ["health_small", "ammo_small", "scrap"],
            "uncommon": ["health_medium", "ammo_medium", "component"],
            "rare": ["health_large", "ammo_large", "artifact"],
            "legendary": ["powerup", "key", "special"]
        }
        return random.choice(loot_types.get(rarity, ["scrap"]))
    
    def get_spawn_positions(self) -> List[Tuple[int, int]]:
        """Get valid spawn positions in the zone."""
        positions = []
        
        # Find platform tiles that could be spawn points
        for tile in self.tiles:
            if tile.type in ["platform_middle", "platform_glow"]:
                positions.append((tile.x, tile.y - 1))  # Position above platform
        
        return positions
    
    def get_enemy_spawns(self) -> List[Dict]:
        """Get enemy spawn data for the zone."""
        spawns = []
        
        for enemy in self.enemies:
            spawn = {
                "type": enemy.type,
                "x": enemy.x * 32,  # Convert to pixel coordinates
                "y": enemy.y * 32,
                "patrol_points": [(x * 32, y * 32) for x, y in enemy.patrol_points] if enemy.patrol_points else None
            }
            spawns.append(spawn)
        
        return spawns
    
    def get_loot_spawns(self) -> List[Dict]:
        """Get loot spawn data for the zone."""
        spawns = []
        
        for loot in self.loot:
            spawn = {
                "rarity": loot.rarity,
                "type": loot.type,
                "x": loot.x * 32,  # Convert to pixel coordinates
                "y": loot.y * 32
            }
            spawns.append(spawn)
        
        return spawns

# Predefined zone templates
ZONE_TEMPLATES = {
    "platform_sequence": {
        "name": "platform_sequence",
        "biome": None,  # Will be set based on biome
        "width": 10,
        "height": 8,
        "layers": [
            ["air", "air", "air", "air", "air", "air", "air", "air", "air", "air"],
            ["air", "air", "platform_left_grass", "platform_middle_grass", "platform_middle_grass", "platform_right_grass", "air", "air", "air", "air"],
            ["air", "air", "support", "support", "support", "support", "air", "air", "air", "air"],
            ["air", "air", "air", "air", "air", "air", "air", "air", "air", "air"],
            ["air", "platform_left_ice", "platform_middle_ice", "platform_right_ice", "air", "air", "platform_left_damaged", "platform_middle_damaged", "platform_right_damaged", "air"],
            ["air", "support", "support", "support", "air", "air", "support", "support", "support", "air"],
            ["air", "air", "air", "air", "air", "air", "air", "air", "air", "air"],
            ["background", "background", "background", "background", "background", "background", "background", "background", "background", "background"]
        ],
        "decorations": [
            {"type": "crystal", "x": 3, "y": 1},
            {"type": "plant", "x": 7, "y": 4}
        ],
        "hazards": [
            {"type": "spikes", "x": 4, "y": 1},
            {"type": "laser", "x": 8, "y": 4}
        ],
        "loot_spawns": [
            {"type": "common", "x": 3, "y": 1},
            {"type": "rare", "x": 7, "y": 4}
        ],
        "enemy_spawns": [
            {"type": "basic", "x": 4, "y": 1},
            {"type": "elite", "x": 8, "y": 4}
        ]
    },
    "floating_islands": {
        "name": "floating_islands",
        "biome": None,
        "width": 12,
        "height": 10,
        "layers": [
            ["air"] * 12,
            ["air", "air", "platform_left_grass", "platform_middle_grass", "platform_right_grass", "air", "air", "air", "air", "air", "air", "air"],
            ["air", "air", "support", "support", "support", "air", "air", "air", "air", "air", "air", "air"],
            ["air"] * 12,
            ["air", "air", "air", "air", "air", "platform_left_ice", "platform_middle_ice", "platform_right_ice", "air", "air", "air", "air"],
            ["air", "air", "air", "air", "air", "support", "support", "support", "air", "air", "air", "air"],
            ["air"] * 12,
            ["air", "air", "air", "air", "air", "air", "air", "air", "platform_left_damaged", "platform_middle_damaged", "platform_right_damaged", "air"],
            ["air", "air", "air", "air", "air", "air", "air", "air", "support", "support", "support", "air"],
            ["background"] * 12
        ],
        "decorations": [
            {"type": "crystal", "x": 3, "y": 1},
            {"type": "plant", "x": 6, "y": 4},
            {"type": "crystal", "x": 9, "y": 7}
        ],
        "hazards": [
            {"type": "spikes", "x": 4, "y": 1},
            {"type": "laser", "x": 7, "y": 4},
            {"type": "spikes", "x": 10, "y": 7}
        ],
        "loot_spawns": [
            {"type": "common", "x": 3, "y": 1},
            {"type": "rare", "x": 6, "y": 4},
            {"type": "epic", "x": 9, "y": 7}
        ],
        "enemy_spawns": [
            {"type": "basic", "x": 4, "y": 1},
            {"type": "elite", "x": 7, "y": 4},
            {"type": "boss", "x": 10, "y": 7}
        ]
    }
}

class ZoneTemplateGenerator:
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        if seed is not None:
            random.seed(seed)
    
    def generate_zone(self, template_name: str, biome: str) -> ZoneTemplate:
        """Generate a zone from a template."""
        if template_name not in ZONE_TEMPLATES:
            raise ValueError(f"Unknown template: {template_name}")
        
        template_data = ZONE_TEMPLATES[template_name].copy()
        template_data["biome"] = biome
        
        # Apply biome variations
        self._apply_biome_variations(template_data, biome)
        
        # Add procedural variations
        self._add_procedural_variations(template_data)
        
        # Create tiles from layers
        tiles = []
        for y, row in enumerate(template_data["layers"]):
            for x, tile_type in enumerate(row):
                if tile_type != "air" and tile_type != "background":
                    tiles.append(ZoneTemplate._create_tile(tile_type, x, y))
        
        # Create decorations
        decorations = [
            ZoneDecoration(type=dec["type"], x=dec["x"], y=dec["y"])
            for dec in template_data.get("decorations", [])
        ]
        
        # Create enemies
        enemies = [
            ZoneEnemy(
                type=enemy["type"],
                x=enemy["x"],
                y=enemy["y"],
                patrol_points=[]
            )
            for enemy in template_data.get("enemy_spawns", [])
        ]
        
        # Create loot
        loot = [
            ZoneLoot(
                type=loot["type"],
                rarity=loot.get("rarity", "common"),
                x=loot["x"],
                y=loot["y"]
            )
            for loot in template_data.get("loot_spawns", [])
        ]
        
        return ZoneTemplate(
            name=template_data["name"],
            biome=biome,
            width=template_data["width"],
            height=template_data["height"],
            tiles=tiles,
            decorations=decorations,
            enemies=enemies,
            loot=loot,
            events=template_data.get("events", []),
            spawn_zone=template_data.get("spawn_zone", False),
            transition_type=template_data.get("transition_type"),
            zone_type=template_data.get("zone_type")
        )
    
    def _apply_biome_variations(self, template: Dict, biome: str):
        """Apply biome-specific variations to the template."""
        # Modify decorations based on biome
        for decoration in template["decorations"]:
            if decoration["type"] in ["crystal", "plant"]:
                decoration["type"] = f"{biome}_{decoration['type']}"
        
        # Modify hazards based on biome
        for hazard in template["hazards"]:
            if hazard["type"] in ["spikes", "laser"]:
                hazard["type"] = f"{biome}_{hazard['type']}"
    
    def _add_procedural_variations(self, template: Dict):
        """Add procedural variations to the template."""
        # Add random height variations to platforms
        for y in range(len(template["layers"])):
            for x in range(len(template["layers"][y])):
                if template["layers"][y][x] in ["platform_left", "platform_middle", "platform_right"]:
                    if random.random() < 0.3:  # 30% chance to add a decoration
                        template["decorations"].append({
                            "type": random.choice(["crystal", "plant"]),
                            "x": x,
                            "y": y
                        })
        
        # Add random hazards
        for y in range(len(template["layers"])):
            for x in range(len(template["layers"][y])):
                if template["layers"][y][x] in ["platform_left", "platform_middle", "platform_right"]:
                    if random.random() < 0.2:  # 20% chance to add a hazard
                        template["hazards"].append({
                            "type": random.choice(["spikes", "laser"]),
                            "x": x,
                            "y": y
                        })
        
        # Add random loot spawns
        for y in range(len(template["layers"])):
            for x in range(len(template["layers"][y])):
                if template["layers"][y][x] in ["platform_left", "platform_middle", "platform_right"]:
                    if random.random() < 0.1:  # 10% chance to add loot
                        template["loot_spawns"].append({
                            "type": random.choice(["common", "rare", "epic"]),
                            "x": x,
                            "y": y
                        })
        
        # Add random enemy spawns
        for y in range(len(template["layers"])):
            for x in range(len(template["layers"][y])):
                if template["layers"][y][x] in ["platform_left", "platform_middle", "platform_right"]:
                    if random.random() < 0.15:  # 15% chance to add an enemy
                        template["enemy_spawns"].append({
                            "type": random.choice(["basic", "elite", "boss"]),
                            "x": x,
                            "y": y
                        }) 