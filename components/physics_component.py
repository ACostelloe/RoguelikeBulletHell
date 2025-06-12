"""
Physics component for entity physics properties.
"""
from typing import Dict, Any, TYPE_CHECKING
from base import Component

if TYPE_CHECKING:
    from entities import Entity

class PhysicsComponent(Component):
    """Component for entity physics properties."""
    def __init__(self, entity: 'Entity', mass: float = 1.0, friction: float = 0.1):
        """Initialize physics component.
        
        Args:
            entity: The entity this component belongs to
            mass: Mass of the entity
            friction: Friction coefficient
        """
        super().__init__(entity)
        self.mass = mass
        self.friction = friction
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.acceleration_x = 0.0
        self.acceleration_y = 0.0
        self.force_x = 0.0
        self.force_y = 0.0
        self.is_static = False
        
    def apply_force(self, force_x: float, force_y: float) -> None:
        """Apply a force to the entity.
        
        Args:
            force_x: Force in x direction
            force_y: Force in y direction
        """
        if not self.is_static:
            self.force_x += force_x
            self.force_y += force_y
            
    def apply_impulse(self, impulse_x: float, impulse_y: float) -> None:
        """Apply an impulse to the entity.
        
        Args:
            impulse_x: Impulse in x direction
            impulse_y: Impulse in y direction
        """
        if not self.is_static:
            self.velocity_x += impulse_x / self.mass
            self.velocity_y += impulse_y / self.mass
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "mass": self.mass,
            "friction": self.friction,
            "velocity_x": self.velocity_x,
            "velocity_y": self.velocity_y,
            "acceleration_x": self.acceleration_x,
            "acceleration_y": self.acceleration_y,
            "force_x": self.force_x,
            "force_y": self.force_y,
            "is_static": self.is_static
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], entity: 'Entity') -> 'PhysicsComponent':
        """Create component from dictionary."""
        component = cls(
            entity=entity,
            mass=data.get("mass", 1.0),
            friction=data.get("friction", 0.1)
        )
        component.velocity_x = data.get("velocity_x", 0.0)
        component.velocity_y = data.get("velocity_y", 0.0)
        component.acceleration_x = data.get("acceleration_x", 0.0)
        component.acceleration_y = data.get("acceleration_y", 0.0)
        component.force_x = data.get("force_x", 0.0)
        component.force_y = data.get("force_y", 0.0)
        component.is_static = data.get("is_static", False)
        return component 