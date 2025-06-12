from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any
import pygame
import json
from enum import Enum, auto

class ZoneType(Enum):
    """Types of zones in the game."""
    EARLY_GAME = auto()
    MID_GAME = auto()
    LATE_GAME = auto()
    BOSS = auto()
    SECRET = auto()
    SHOP = auto()
    TREASURE = auto()
    CHALLENGE = auto()

class BiomeType(Enum):
    """Types of biomes in the game."""
    FOREST = auto()
    DESERT = auto()
    SNOW = auto()
    VOLCANO = auto()
    CAVE = auto()
    CRYSTAL = auto()
    CORRUPTED = auto()
    HEAVENLY = auto()

@dataclass
class ZoneTile:
    """Represents a tile in a zone."""
    x: int
    y: int
    type: str
    is_platform: bool = False
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert tile to dictionary."""
        return {
            "x": self.x,
            "y": self.y,
            "type": self.type,
            "is_platform": self.is_platform,
            "properties": self.properties
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ZoneTile':
        """Create tile from dictionary."""
        return cls(
            x=data["x"],
            y=data["y"],
            type=data["type"],
            is_platform=data.get("is_platform", False),
            properties=data.get("properties", {})
        )

@dataclass
class ZoneDecoration:
    """Represents a decoration in a zone."""
    x: int
    y: int
    type: str
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert decoration to dictionary."""
        return {
            "x": self.x,
            "y": self.y,
            "type": self.type,
            "properties": self.properties
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ZoneDecoration':
        """Create decoration from dictionary."""
        return cls(
            x=data["x"],
            y=data["y"],
            type=data["type"],
            properties=data.get("properties", {})
        )

@dataclass
class ZoneEnemy:
    """Represents an enemy in a zone."""
    x: int
    y: int
    type: str
    patrol_points: List[Dict[str, int]] = None
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.patrol_points is None:
            self.patrol_points = []
        if self.properties is None:
            self.properties = {}
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert enemy to dictionary."""
        return {
            "x": self.x,
            "y": self.y,
            "type": self.type,
            "patrol_points": self.patrol_points,
            "properties": self.properties
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ZoneEnemy':
        """Create enemy from dictionary."""
        return cls(
            x=data["x"],
            y=data["y"],
            type=data["type"],
            patrol_points=data.get("patrol_points", []),
            properties=data.get("properties", {})
        )

@dataclass
class ZoneLoot:
    """Represents loot in a zone."""
    type: str
    x: int
    y: int
    rarity: str = "common"
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert loot to dictionary."""
        return {
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "rarity": self.rarity,
            "properties": self.properties
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ZoneLoot':
        """Create loot from dictionary."""
        return cls(
            type=data["type"],
            x=data["x"],
            y=data["y"],
            rarity=data.get("rarity", "common"),
            properties=data.get("properties", {})
        )

@dataclass
class ZoneTransition:
    """Represents a transition in a zone."""
    type: str
    x: int
    y: int
    target: str
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert transition to dictionary."""
        return {
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "target": self.target,
            "properties": self.properties
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ZoneTransition':
        """Create transition from dictionary."""
        return cls(
            type=data["type"],
            x=data["x"],
            y=data["y"],
            target=data["target"],
            properties=data.get("properties", {})
        )

@dataclass
class ZoneTemplate:
    """Represents a zone template."""
    name: str
    biome: str
    zone_type: str
    width: int
    height: int
    tiles: List[ZoneTile]
    decorations: List[ZoneDecoration]
    enemies: List[ZoneEnemy]
    loot: List[ZoneLoot]
    events: List[Dict[str, Any]]
    spawn_zone: bool
    transition_type: Optional[str]
    transitions: List[ZoneTransition]
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary."""
        return {
            "name": self.name,
            "biome": self.biome,
            "zone_type": self.zone_type,
            "width": self.width,
            "height": self.height,
            "tiles": [tile.to_dict() for tile in self.tiles],
            "decorations": [dec.to_dict() for dec in self.decorations],
            "enemies": [enemy.to_dict() for enemy in self.enemies],
            "loot": [item.to_dict() for item in self.loot],
            "events": self.events,
            "spawn_zone": self.spawn_zone,
            "transition_type": self.transition_type,
            "transitions": [trans.to_dict() for trans in self.transitions],
            "properties": self.properties
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ZoneTemplate':
        """Create template from dictionary."""
        return cls(
            name=data["name"],
            biome=data["biome"],
            zone_type=data["zone_type"],
            width=data["width"],
            height=data["height"],
            tiles=[ZoneTile.from_dict(tile) for tile in data["tiles"]],
            decorations=[ZoneDecoration.from_dict(dec) for dec in data.get("decorations", [])],
            enemies=[ZoneEnemy.from_dict(enemy) for enemy in data.get("enemies", [])],
            loot=[ZoneLoot.from_dict(item) for item in data.get("loot", [])],
            events=data.get("events", []),
            spawn_zone=data.get("spawn_zone", False),
            transition_type=data.get("transition_type"),
            transitions=[ZoneTransition.from_dict(trans) for trans in data.get("transitions", [])],
            properties=data.get("properties", {})
        )
        
    def to_json(self) -> str:
        """Convert template to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
        
    @classmethod
    def from_json(cls, json_str: str) -> 'ZoneTemplate':
        """Create template from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
        
    def validate(self) -> bool:
        """Validate the template's structure and data."""
        try:
            # Check required fields
            if not all([self.name, self.biome, self.zone_type, self.width, self.height]):
                return False
                
            # Validate dimensions
            if self.width <= 0 or self.height <= 0:
                return False
                
            # Validate tiles
            for tile in self.tiles:
                if not (0 <= tile.x < self.width and 0 <= tile.y < self.height):
                    return False
                    
            # Validate decorations
            for dec in self.decorations:
                if not (0 <= dec.x < self.width and 0 <= dec.y < self.height):
                    return False
                    
            # Validate enemies
            for enemy in self.enemies:
                if not (0 <= enemy.x < self.width and 0 <= enemy.y < self.height):
                    return False
                    
            # Validate loot
            for item in self.loot:
                if not (0 <= item.x < self.width and 0 <= item.y < self.height):
                    return False
                    
            # Validate transitions
            for trans in self.transitions:
                if not (0 <= trans.x < self.width and 0 <= trans.y < self.height):
                    return False
                    
            return True
            
        except Exception:
            return False
            
    def get_tile_at(self, x: int, y: int) -> Optional[ZoneTile]:
        """Get tile at specified coordinates."""
        for tile in self.tiles:
            if tile.x == x and tile.y == y:
                return tile
        return None
        
    def get_decorations_at(self, x: int, y: int) -> List[ZoneDecoration]:
        """Get decorations at specified coordinates."""
        return [dec for dec in self.decorations if dec.x == x and dec.y == y]
        
    def get_enemies_at(self, x: int, y: int) -> List[ZoneEnemy]:
        """Get enemies at specified coordinates."""
        return [enemy for enemy in self.enemies if enemy.x == x and enemy.y == y]
        
    def get_loot_at(self, x: int, y: int) -> List[ZoneLoot]:
        """Get loot at specified coordinates."""
        return [item for item in self.loot if item.x == x and item.y == y]
        
    def get_transitions_at(self, x: int, y: int) -> List[ZoneTransition]:
        """Get transitions at specified coordinates."""
        return [trans for trans in self.transitions if trans.x == x and trans.y == y]
        
    def add_tile(self, tile: ZoneTile) -> None:
        """Add a tile to the template."""
        if 0 <= tile.x < self.width and 0 <= tile.y < self.height:
            self.tiles.append(tile)
            
    def add_decoration(self, decoration: ZoneDecoration) -> None:
        """Add a decoration to the template."""
        if 0 <= decoration.x < self.width and 0 <= decoration.y < self.height:
            self.decorations.append(decoration)
            
    def add_enemy(self, enemy: ZoneEnemy) -> None:
        """Add an enemy to the template."""
        if 0 <= enemy.x < self.width and 0 <= enemy.y < self.height:
            self.enemies.append(enemy)
            
    def add_loot(self, loot: ZoneLoot) -> None:
        """Add loot to the template."""
        if 0 <= loot.x < self.width and 0 <= loot.y < self.height:
            self.loot.append(loot)
            
    def add_transition(self, transition: ZoneTransition) -> None:
        """Add a transition to the template."""
        if 0 <= transition.x < self.width and 0 <= transition.y < self.height:
            self.transitions.append(transition)
            
    def remove_tile(self, x: int, y: int) -> None:
        """Remove tile at specified coordinates."""
        self.tiles = [tile for tile in self.tiles if not (tile.x == x and tile.y == y)]
        
    def remove_decoration(self, x: int, y: int) -> None:
        """Remove decoration at specified coordinates."""
        self.decorations = [dec for dec in self.decorations if not (dec.x == x and dec.y == y)]
        
    def remove_enemy(self, x: int, y: int) -> None:
        """Remove enemy at specified coordinates."""
        self.enemies = [enemy for enemy in self.enemies if not (enemy.x == x and enemy.y == y)]
        
    def remove_loot(self, x: int, y: int) -> None:
        """Remove loot at specified coordinates."""
        self.loot = [item for item in self.loot if not (item.x == x and item.y == y)]
        
    def remove_transition(self, x: int, y: int) -> None:
        """Remove transition at specified coordinates."""
        self.transitions = [trans for trans in self.transitions if not (trans.x == x and trans.y == y)]

@dataclass
class Zone:
    """Represents a zone in the game world."""
    id: str  # Unique identifier for the zone
    template: 'ZoneTemplate'  # The template used to generate this zone
    x: int  # World x coordinate
    y: int  # World y coordinate
    entities: List[str] = field(default_factory=list)  # List of entity IDs in this zone
    is_active: bool = True  # Whether the zone is currently active/loaded
    
    def get_world_position(self) -> Tuple[int, int]:
        """Get the world position of this zone."""
        return (self.x, self.y)
    
    def get_screen_position(self, camera_x: float, camera_y: float) -> Tuple[int, int]:
        """Get the screen position of this zone relative to the camera."""
        return (self.x - camera_x, self.y - camera_y)
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if a point is within this zone."""
        zone_size = self.template.width * 32  # Assuming 32 is tile size
        return (self.x <= x < self.x + zone_size and 
                self.y <= y < self.y + zone_size)
    
    def add_entity(self, entity_id: str) -> None:
        """Add an entity to this zone."""
        if entity_id not in self.entities:
            self.entities.append(entity_id)
    
    def remove_entity(self, entity_id: str) -> None:
        """Remove an entity from this zone."""
        if entity_id in self.entities:
            self.entities.remove(entity_id) 