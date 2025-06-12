from typing import List, Optional, Dict, Any
from zone_template import ZoneTemplate
from zone_types import ZoneTile, ZoneDecoration, ZoneEnemy, ZoneLoot, ZoneTransition
import logging
import json

logger = logging.getLogger(__name__)

class Zone:
    def __init__(self, id: str, template: ZoneTemplate, x: int, y: int):
        self.id = id
        self.template = template
        self.x = x
        self.y = y
        
        self.name = template.name
        self.biome = template.biome
        self.zone_type = template.zone_type
        self.width = template.width
        self.height = template.height

        self.tiles: List[ZoneTile] = template.tiles
        self.decorations: List[ZoneDecoration] = template.decorations
        self.enemies: List[ZoneEnemy] = template.enemies
        self.loot: List[ZoneLoot] = template.loot
        self.transitions: List[ZoneTransition] = template.transitions
        self.events: List[str] = template.events

        self.spawn_zone = template.spawn_zone
        self.transition_type = template.transition_type

        self.entities = []  # Entities spawned into this zone
        self.state: Dict[str, Any] = {}  # Zone state
        
        logger.info(f"Created zone {id} at ({x}, {y})")

    def get_tile_at(self, x: int, y: int) -> Optional[ZoneTile]:
        """Get tile at specified coordinates."""
        for tile in self.tiles:
            if tile.x == x and tile.y == y:
                return tile
        return None

    def add_entity(self, entity_id: str) -> None:
        """Add an entity to this zone."""
        if entity_id not in self.entities:
            self.entities.append(entity_id)
            logger.debug(f"Added entity {entity_id} to zone {self.id}")

    def remove_entity(self, entity_id: str) -> None:
        """Remove an entity from this zone."""
        if entity_id in self.entities:
            self.entities.remove(entity_id)
            logger.debug(f"Removed entity {entity_id} from zone {self.id}")

    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the zone."""
        return {
            'id': self.id,
            'name': self.name,
            'biome': self.biome,
            'zone_type': self.zone_type,
            'x': self.x,
            'y': self.y,
            'entities': self.entities,
            'state': self.state
        }

    def set_state(self, state: Dict[str, Any]) -> None:
        """Set the state of the zone."""
        try:
            self.id = state.get('id', self.id)
            self.name = state.get('name', self.name)
            self.biome = state.get('biome', self.biome)
            self.zone_type = state.get('zone_type', self.zone_type)
            self.x = state.get('x', self.x)
            self.y = state.get('y', self.y)
            self.entities = state.get('entities', self.entities)
            self.state = state.get('state', self.state)
            logger.info(f"Updated state for zone {self.id}")
        except Exception as e:
            logger.error(f"Error setting state for zone {self.id}: {str(e)}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """Convert zone to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'biome': self.biome,
            'zone_type': self.zone_type,
            'x': self.x,
            'y': self.y,
            'entities': self.entities,
            'state': self.state,
            'template': self.template.name
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], template: ZoneTemplate) -> 'Zone':
        """Create a zone from dictionary data."""
        zone = cls(
            id=data['id'],
            template=template,
            x=data['x'],
            y=data['y']
        )
        zone.entities = data.get('entities', [])
        zone.state = data.get('state', {})
        return zone 