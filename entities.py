"""
Entities module.
"""
from typing import Dict, List, Tuple, Optional, Any, Type, TypeVar, Generic, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import pygame
import json
import uuid
import traceback
from base import Component
from utils import ComponentRegistry
from logger import logger
from components import StateComponent, TransformComponent

T = TypeVar('T')

class EntityType(Enum):
    """Types of entities in the game."""
    PLAYER = auto()
    ENEMY = auto()
    BULLET = auto()
    LOOT = auto()
    DECORATION = auto()
    EFFECT = auto()
    TRIGGER = auto()
    UI = auto()  # Added UI type for UI elements
    ZONE = auto()  # Added ZONE type for zone entities

class EntityState(Enum):
    """States for entities."""
    IDLE = auto()
    MOVING = auto()
    ATTACKING = auto()
    HURT = auto()
    DEAD = auto()
    STUNNED = auto()
    INVINCIBLE = auto()

class StatusEffectType(Enum):
    """Types of status effects."""
    POISON = auto()
    BURN = auto()
    FREEZE = auto()
    STUN = auto()
    SLOW = auto()
    SPEED_UP = auto()
    DAMAGE_UP = auto()
    DEFENSE_UP = auto()

@dataclass
class StatusEffect:
    """Represents a status effect on an entity."""
    type: StatusEffectType
    duration: float
    value: float = 0.0
    tick_rate: float = 1.0
    time_since_last_tick: float = 0.0
    
    def update(self, dt: float) -> None:
        """Update the status effect."""
        self.duration -= dt
        self.time_since_last_tick += dt
        
        if self.time_since_last_tick >= self.tick_rate:
            self.time_since_last_tick = 0.0
            return True
        return False
    
    def is_expired(self) -> bool:
        """Check if the status effect has expired."""
        return self.duration <= 0.0

@dataclass
class Component:
    """Base class for entity components."""
    entity: 'Entity'
    
    def update(self, dt: float) -> None:
        """Update the component."""
        pass
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {}
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], entity: 'Entity') -> 'Component':
        """Create component from dictionary."""
        return cls(entity)

@dataclass
class PhysicsComponent(Component):
    """Component for entity physics."""
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    acceleration_x: float = 0.0
    acceleration_y: float = 0.0
    mass: float = 1.0
    friction: float = 0.1
    gravity: float = 0.0
    is_kinematic: bool = False
    
    def update(self, dt: float) -> None:
        """Update physics."""
        if not self.is_kinematic:
            # Apply gravity
            self.velocity_y += self.gravity * dt
            
            # Apply acceleration
            self.velocity_x += self.acceleration_x * dt
            self.velocity_y += self.acceleration_y * dt
            
            # Apply friction
            if abs(self.velocity_x) > 0:
                self.velocity_x *= (1 - self.friction)
            if abs(self.velocity_y) > 0:
                self.velocity_y *= (1 - self.friction)
                
            # Update position
            transform = self.entity.get_component(TransformComponent)
            if transform:
                transform.x += self.velocity_x * dt
                transform.y += self.velocity_y * dt
                
    def to_dict(self) -> Dict[str, Any]:
        """Convert physics to dictionary."""
        return {
            "velocity_x": self.velocity_x,
            "velocity_y": self.velocity_y,
            "acceleration_x": self.acceleration_x,
            "acceleration_y": self.acceleration_y,
            "mass": self.mass,
            "friction": self.friction,
            "gravity": self.gravity,
            "is_kinematic": self.is_kinematic
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], entity: 'Entity') -> 'PhysicsComponent':
        """Create physics from dictionary."""
        return cls(
            entity=entity,
            velocity_x=data["velocity_x"],
            velocity_y=data["velocity_y"],
            acceleration_x=data["acceleration_x"],
            acceleration_y=data["acceleration_y"],
            mass=data["mass"],
            friction=data["friction"],
            gravity=data["gravity"],
            is_kinematic=data["is_kinematic"]
        )

@dataclass
class CollisionComponent(Component):
    """Component for entity collision."""
    width: float = 32.0
    height: float = 32.0
    is_trigger: bool = False
    collision_mask: int = 0xFFFFFFFF
    collision_layer: int = 0x00000001
    
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        transform = self.entity.get_component(TransformComponent)
        if transform:
            return pygame.Rect(
                transform.x - self.width / 2,
                transform.y - self.height / 2,
                self.width,
                self.height
            )
        return pygame.Rect(0, 0, self.width, self.height)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert collision to dictionary."""
        return {
            "width": self.width,
            "height": self.height,
            "is_trigger": self.is_trigger,
            "collision_mask": self.collision_mask,
            "collision_layer": self.collision_layer
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], entity: 'Entity') -> 'CollisionComponent':
        """Create collision from dictionary."""
        return cls(
            entity=entity,
            width=data["width"],
            height=data["height"],
            is_trigger=data["is_trigger"],
            collision_mask=data["collision_mask"],
            collision_layer=data["collision_layer"]
        )

class Entity:
    """Base class for all game entities."""
    
    def __init__(self, entity_type: EntityType, name: str = ""):
        """Initialize entity."""
        self.id = str(uuid.uuid4())
        self.name = name or f"{entity_type.name}_{self.id[:8]}"
        self.type = entity_type
        self.components: Dict[str, Component] = {}
        self.children: List['Entity'] = []
        self.parent: Optional['Entity'] = None
        self.status_effects: List[StatusEffect] = []
        self.dead = False
        self.zone_id: Optional[str] = None
        self.tags: Set[str] = set()  # Initialize empty tags set
        self.active = True  # Add active attribute
        
        # Automatically add required components
        self.add_component(TransformComponent(self))
        self.add_component(StateComponent(self))
        
    def add_component(self, component: Component) -> None:
        """Add a component to the entity."""
        component_name = component.__class__.__name__
        self.components[component_name] = component
        
    def remove_component(self, component_name: str) -> None:
        """Remove a component from the entity."""
        if component_name in self.components:
            del self.components[component_name]
            
    def get_component(self, component_type: Type[T]) -> Optional[T]:
        """Get a component by type."""
        component_name = component_type.__name__
        return self.components.get(component_name)
        
    def has_component(self, component_name: str) -> bool:
        """Check if entity has a component."""
        return component_name in self.components
        
    def set_state(self, new_state: str, reason: Optional[str] = None) -> bool:
        """Set entity state.
        
        Args:
            new_state: New state to set
            reason: Optional reason for state change
            
        Returns:
            bool: True if state was changed successfully
        """
        state_component = self.get_component(StateComponent)
        if state_component:
            return state_component.set_state(new_state, reason)
        return False
        
    def get_state(self) -> Optional[str]:
        """Get current entity state.
        
        Returns:
            Optional[str]: Current state or None if no state component
        """
        state_component = self.get_component(StateComponent)
        if state_component:
            return state_component.current_state
        return None
        
    def get_state_time(self) -> float:
        """Get time spent in current state.
        
        Returns:
            float: Time in current state or 0.0 if no state component
        """
        state_component = self.get_component(StateComponent)
        if state_component:
            return state_component.state_time
        return 0.0
        
    def get_state_history(self) -> List[Dict[str, Any]]:
        """Get state transition history.
        
        Returns:
            List[Dict[str, Any]]: List of state transitions
        """
        state_component = self.get_component(StateComponent)
        if state_component:
            return [
                {
                    "from_state": t.from_state,
                    "to_state": t.to_state,
                    "timestamp": t.timestamp.isoformat(),
                    "reason": t.reason
                }
                for t in state_component.get_state_history()
            ]
        return []
        
    def update(self, dt: float) -> None:
        """Update entity and all its components."""
        if not self.active:
            return
            
        # Update components
        for component in self.components.values():
            try:
                component.update(dt)
            except Exception as e:
                logger.error(f"Error updating component {component.__class__.__name__} for entity {self.id}: {str(e)}")
                logger.error(traceback.format_exc())
                
        # Update children
        for child in self.children:
            child.update(dt)
            
    def draw(self, surface: pygame.Surface) -> None:
        """Draw entity and all its components."""
        if not self.active:
            return
            
        # Draw components
        for component in self.components.values():
            try:
                if hasattr(component, 'draw'):
                    component.draw(surface)
            except Exception as e:
                logger.error(f"Error drawing component {component.__class__.__name__} for entity {self.id}: {str(e)}")
                logger.error(traceback.format_exc())
                
        # Draw children
        for child in self.children:
            child.draw(surface)
            
    def on_spawn(self) -> None:
        """Called when entity is added to the world."""
        pass
        
    def on_despawn(self) -> None:
        """Called when entity is removed from the world."""
        pass
        
    def on_zone_enter(self, zone_id: str) -> None:
        """Called when entity enters a zone."""
        self.zone_id = zone_id
        
    def on_zone_exit(self, zone_id: str) -> None:
        """Called when entity exits a zone."""
        if self.zone_id == zone_id:
            self.zone_id = None
            
    def add_child(self, child: 'Entity') -> None:
        """Add a child entity."""
        self.children.append(child)
        child.parent = self
        
    def remove_child(self, child: 'Entity') -> None:
        """Remove a child entity."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.name,
            "active": self.active,
            "zone_id": self.zone_id,
            "tags": list(self.tags),
            "components": {
                name: component.to_dict()
                for name, component in self.components.items()
            },
            "children": [child.to_dict() for child in self.children]
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create entity from dictionary."""
        entity = cls(EntityType[data["type"]], data["name"])
        entity.active = data["active"]
        entity.zone_id = data["zone_id"]
        entity.tags = set(data["tags"])
        
        # Load components
        for component_name, component_data in data["components"].items():
            component_type = ComponentRegistry.get_component_type(component_name)
            if component_type:
                component = component_type.from_dict(component_data, entity)
                entity.add_component(component)
                
        # Load children
        for child_data in data["children"]:
            child = cls.from_dict(child_data)
            entity.add_child(child)
            
        return entity
        
    def save_to_file(self, file_path: str) -> None:
        """Save entity to file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
            
    @classmethod
    def load_from_file(cls, file_path: str) -> 'Entity':
        """Load entity from file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
        
    def render(self, surface, camera):
        # This is a placeholder. Actual rendering is likely handled by a renderer system.
        pass 