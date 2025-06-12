"""
Zone Template Loader module.
"""
import json
import os
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from zone_template import ZoneTemplate
from zone_types import ZoneTile, ZoneDecoration, ZoneEnemy, ZoneLoot, ZoneTransition
import random
from logger import logger
import traceback

class TemplateValidationError(Exception):
    """Raised when template validation fails."""
    pass

class TemplateVersionError(Exception):
    """Raised when template version is incompatible."""
    pass

@dataclass
class TemplateMetadata:
    """Metadata for a zone template."""
    version: str
    parent: Optional[str] = None
    biome: Optional[str] = None
    zone_type: Optional[str] = None
    tags: Set[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = set()

class ZoneTemplateLoader:
    """Loads and manages zone templates."""
    
    def __init__(self, entity_manager, zones_dir: str = "zones"):
        """Initialize the zone template loader."""
        self.entity_manager = entity_manager
        self.zones_dir = zones_dir
        self.templates: Dict[str, Dict[str, List[ZoneTemplate]]] = {}
        self.load_all_templates()
        
    def load_all_templates(self):
        """Load all zone templates from the zones directory."""
        try:
            for biome in os.listdir(self.zones_dir):
                biome_dir = os.path.join(self.zones_dir, biome)
                if not os.path.isdir(biome_dir):
                    continue
                self.templates[biome] = {}
                for filename in os.listdir(biome_dir):
                    if filename.endswith(".json"):
                        path = os.path.join(biome_dir, filename)
                        with open(path, "r") as f:
                            data = json.load(f)
                            
                            # Convert tiles to ZoneTile objects
                            tiles = []
                            for y, row in enumerate(data["tiles"]):
                                for x, tile_type in enumerate(row):
                                    tiles.append(ZoneTile(type=tile_type, x=x, y=y))
                            
                            # Convert enemies to ZoneEnemy objects
                            enemies = []
                            for enemy_data in data.get("enemies", []):
                                enemies.append(ZoneEnemy(
                                    type=enemy_data["type"],
                                    x=enemy_data["x"],
                                    y=enemy_data["y"]
                                ))
                            
                            # Convert loot to ZoneLoot objects
                            loot = []
                            for loot_data in data.get("loot", []):
                                loot.append(ZoneLoot(
                                    type=loot_data.get("type", "common"),
                                    x=loot_data["x"],
                                    y=loot_data["y"],
                                    rarity=loot_data.get("rarity", "common")
                                ))
                            
                            # Convert decorations to ZoneDecoration objects
                            decorations = []
                            for dec_data in data.get("decorations", []):
                                decorations.append(ZoneDecoration(
                                    type=dec_data["type"],
                                    x=dec_data["x"],
                                    y=dec_data["y"]
                                ))
                            
                            # Create the template
                            template = ZoneTemplate(
                                name=data["name"],
                                biome=data["biome"],
                                width=len(data["tiles"][0]),
                                height=len(data["tiles"]),
                                tiles=tiles,
                                enemies=enemies,
                                loot=loot,
                                decorations=decorations,
                                zone_type=data.get("zone_type", "normal")
                            )
                            
                            zone_type = data.get("zone_type", "normal")
                            if zone_type not in self.templates[biome]:
                                self.templates[biome][zone_type] = []
                            self.templates[biome][zone_type].append(template)
        except Exception as e:
            logger.error(f"Error loading zone templates: {str(e)}")
            logger.error(traceback.format_exc())
            
    def get_random_template(self, biome: str, zone_type: str = "normal") -> ZoneTemplate:
        """Get a random template for the given biome and type."""
        if biome not in self.templates or zone_type not in self.templates[biome]:
            raise ValueError(f"No template found for biome '{biome}' and zone_type '{zone_type}'")
        return random.choice(self.templates[biome][zone_type])
        
    def get_template(self, biome: str, name: str) -> ZoneTemplate:
        """Get a zone template by biome and name."""
        for zone_type in self.templates.get(biome, {}).values():
            for template in zone_type:
                if template.name == name:
                    return template
        raise ValueError(f"No template found for biome '{biome}' and name '{name}'")
        
    def get_templates_by_biome(self, biome: str) -> List[ZoneTemplate]:
        """Get all templates for a biome."""
        templates = []
        if biome in self.templates:
            for type_templates in self.templates[biome].values():
                templates.extend(type_templates)
        return templates
        
    def get_templates_by_type(self, zone_type: str) -> List[ZoneTemplate]:
        """Get all templates of a specific type across all biomes."""
        templates = []
        for biome_templates in self.templates.values():
            if zone_type in biome_templates:
                templates.extend(biome_templates[zone_type])
        return templates
        
    def get_template_by_name(self, name: str) -> Optional[ZoneTemplate]:
        """Get a template by its name."""
        for biome_templates in self.templates.values():
            for type_templates in biome_templates.values():
                for template in type_templates:
                    if template.name == name:
                        return template
        return None
        
    def reload_templates(self) -> None:
        """Reload all templates from disk."""
        self.templates.clear()
        self.load_all_templates() 