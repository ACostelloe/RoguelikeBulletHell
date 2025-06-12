"""
JSON Zone Template Loader module.
"""
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from zone_types import ZoneTile, ZoneDecoration, ZoneEnemy, ZoneLoot, ZoneTransition

class JSONZoneLoader:
    def __init__(self, zones_directory: str = "zones"):
        self.zones_directory = zones_directory
        self._ensure_zones_directory()
    
    def _ensure_zones_directory(self):
        """Ensure the zones directory exists."""
        if not os.path.exists(self.zones_directory):
            os.makedirs(self.zones_directory)
    
    def load_zone_template_from_json(self, file_path: str) -> Optional[ZoneTemplate]:
        """Load a zone template from a JSON file."""
        try:
            print(f"📂 Attempting to load template from: {file_path}")
            
            with open(file_path, 'r') as f:
                raw_data = f.read()
                print(f"📄 JSON content preview: {raw_data[:100]}...")
                data = json.loads(raw_data)
            
            print(f"✅ Keys in template: {list(data.keys())}")
            
            # Parse tiles
            tiles = self._parse_tile_layout(data["tiles"], data["legend"])
            
            # Parse decorations
            decorations = [
                ZoneDecoration(
                    type=dec["type"],
                    x=dec["x"],
                    y=dec["y"],
                    properties=dec.get("properties", {})
                )
                for dec in data.get("decorations", [])
            ]
            
            # Parse enemies
            enemies = [
                ZoneEnemy(
                    type=enemy["type"],
                    x=enemy["x"],
                    y=enemy["y"],
                    patrol_points=enemy.get("patrol_points", [])
                )
                for enemy in data.get("enemies", [])
            ]
            
            # Parse loot
            loot = [
                ZoneLoot(
                    type=loot_data["type"],
                    x=loot_data["x"],
                    y=loot_data["y"],
                    rarity=loot_data.get("rarity", "common")
                )
                for loot_data in data.get("loot", [])
            ]
            
            # Parse transitions
            transitions = [
                ZoneTransition(
                    type=trans["type"],
                    x=trans["x"],
                    y=trans["y"],
                    target=trans["target"]
                )
                for trans in data.get("transitions", [])
            ]
            
            # Create template
            template = ZoneTemplate(
                name=data["name"],
                biome=data["biome"],
                zone_type=data.get("zone_type", data.get("type", "early_game")),
                width=data["width"],
                height=data["height"],
                tiles=tiles,
                decorations=decorations,
                enemies=enemies,
                loot=loot,
                events=data.get("events", []),
                spawn_zone=data.get("spawn_zone", False),
                transition_type=data.get("transition_type"),
                transitions=transitions
            )
            
            print(f"🧠 Registering template for biome: {data['biome']}, zone_type: {data.get('zone_type', data.get('type', 'early_game'))}")
            return template
            
        except Exception as e:
            print(f"❌ Error loading zone template from {file_path}: {e}")
            return None
    
    def _parse_tile_layout(self, layout: List[str], legend: Dict[str, str]) -> List[ZoneTile]:
        """Parse the tile layout into a list of ZoneTile objects."""
        tiles = []
        
        for y, row in enumerate(layout):
            for x, char in enumerate(row):
                if char in legend:
                    tile_type = legend[char]
                    tiles.append(ZoneTile(
                        type=tile_type,
                        x=x,
                        y=y
                    ))
        
        return tiles
    
    def load_all_zone_templates(self) -> Dict[str, ZoneTemplate]:
        """Load all zone templates from the zones directory."""
        templates = {}
        
        for filename in os.listdir(self.zones_directory):
            if filename.endswith('.json'):
                path = os.path.join(self.zones_directory, filename)
                template = self.load_zone_template_from_json(path)
                if template:
                    templates[template.name] = template
        
        print(f"📦 Registered Templates: {list(templates.keys())}")
        return templates

# Example usage:
if __name__ == "__main__":
    loader = JSONZoneLoader()
    templates = loader.load_all_zone_templates()
    print(f"Loaded {len(templates)} zone templates") 