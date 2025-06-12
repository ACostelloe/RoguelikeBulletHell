from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from enum import Enum

class TileCategory(Enum):
    PLATFORM = "platform"
    SUPPORT = "support"
    DECORATION = "decoration"
    HAZARD = "hazard"
    BACKGROUND = "background"

@dataclass
class TileRule:
    category: TileCategory
    connects_to: Set[str]
    must_be_under: Optional[Set[str]] = None
    must_be_above: Optional[Set[str]] = None
    spacing_rules: Optional[Dict[str, int]] = None
    biome_variants: Optional[Dict[str, List[str]]] = None

# Define tile rules for different tile types
TILE_RULES: Dict[str, TileRule] = {
    # Platform tiles
    "platform_left": TileRule(
        category=TileCategory.PLATFORM,
        connects_to={"platform_middle"},
        must_be_under={"support"},
        spacing_rules={"min_width": 1, "max_width": 1}
    ),
    "platform_middle": TileRule(
        category=TileCategory.PLATFORM,
        connects_to={"platform_left", "platform_right", "platform_middle"},
        must_be_under={"support"},
        spacing_rules={"min_width": 1, "max_width": 5}
    ),
    "platform_right": TileRule(
        category=TileCategory.PLATFORM,
        connects_to={"platform_middle"},
        must_be_under={"support"},
        spacing_rules={"min_width": 1, "max_width": 1}
    ),
    
    # Support tiles
    "support": TileRule(
        category=TileCategory.SUPPORT,
        connects_to={"support"},
        must_be_above={"platform_middle", "platform_left", "platform_right"},
        spacing_rules={"min_height": 1, "max_height": 3}
    ),
    
    # Hazard tiles
    "spikes": TileRule(
        category=TileCategory.HAZARD,
        connects_to={"platform_middle", "platform_left", "platform_right"},
        spacing_rules={"min_spacing": 2}
    ),
    "laser": TileRule(
        category=TileCategory.HAZARD,
        connects_to={"platform_middle", "platform_left", "platform_right"},
        spacing_rules={"min_spacing": 3}
    ),
    
    # Decoration tiles
    "crystal": TileRule(
        category=TileCategory.DECORATION,
        connects_to={"platform_middle", "platform_left", "platform_right"},
        spacing_rules={"min_spacing": 2}
    ),
    "plant": TileRule(
        category=TileCategory.DECORATION,
        connects_to={"platform_middle", "platform_left", "platform_right"},
        spacing_rules={"min_spacing": 1}
    ),
    
    # Background tiles
    "background": TileRule(
        category=TileCategory.BACKGROUND,
        connects_to={"background"},
        spacing_rules={"min_spacing": 0}
    )
}

# Biome-specific tile variants
BIOME_VARIANTS = {
    "forest": {
        "platform_left": ["grass_left", "moss_left", "wood_left"],
        "platform_middle": ["grass_middle", "moss_middle", "wood_middle"],
        "platform_right": ["grass_right", "moss_right", "wood_right"],
        "support": ["tree", "vine", "root"],
        "decoration": ["leaf", "flower", "mushroom"]
    },
    "tech": {
        "platform_left": ["metal_left", "circuit_left", "energy_left"],
        "platform_middle": ["metal_middle", "circuit_middle", "energy_middle"],
        "platform_right": ["metal_right", "circuit_right", "energy_right"],
        "support": ["beam", "cable", "strut"],
        "decoration": ["console", "light", "hologram"]
    },
    "ice": {
        "platform_left": ["ice_left", "snow_left", "crystal_left"],
        "platform_middle": ["ice_middle", "snow_middle", "crystal_middle"],
        "platform_right": ["ice_right", "snow_right", "crystal_right"],
        "support": ["icicle", "frost", "pillar"],
        "decoration": ["snowflake", "gem", "aurora"]
    },
    "lava": {
        "platform_left": ["magma_left", "obsidian_left", "ash_left"],
        "platform_middle": ["magma_middle", "obsidian_middle", "ash_middle"],
        "platform_right": ["magma_right", "obsidian_right", "ash_right"],
        "support": ["geyser", "vent", "column"],
        "decoration": ["ember", "crystal", "glow"]
    }
}

def get_tile_variant(tile_type: str, biome: str) -> str:
    """Get a random variant for a tile type in the given biome."""
    if tile_type in BIOME_VARIANTS.get(biome, {}):
        variants = BIOME_VARIANTS[biome][tile_type]
        return random.choice(variants)
    return tile_type

def validate_tile_placement(tile_type: str, neighbors: Dict[str, str]) -> bool:
    """Validate if a tile can be placed next to its neighbors."""
    if tile_type not in TILE_RULES:
        return False
    
    rule = TILE_RULES[tile_type]
    
    # Check connections
    for direction, neighbor_type in neighbors.items():
        if neighbor_type not in rule.connects_to:
            return False
    
    # Check must_be_under rules
    if rule.must_be_under:
        below_tile = neighbors.get("below")
        if below_tile and below_tile not in rule.must_be_under:
            return False
    
    # Check must_be_above rules
    if rule.must_be_above:
        above_tile = neighbors.get("above")
        if above_tile and above_tile not in rule.must_be_above:
            return False
    
    return True 