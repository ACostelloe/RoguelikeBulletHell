"""
Collision component for entity collision detection.
"""
from typing import Dict, Any, TYPE_CHECKING
from base import Component

if TYPE_CHECKING:
    from entities import Entity

class CollisionComponent(Component):
    """Component for entity collision detection."""
    def __init__(self, entity: 'Entity', width: float = 32.0, height: float = 32.0):
        """Initialize collision component.
        
        Args:
            entity: The entity this component belongs to
            width: Width of collision box
            height: Height of collision box
        """
        super().__init__(entity)
        self.width = width
        self.height = height
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.is_trigger = False
        self.collision_mask = 0xFFFFFFFF  # All layers
        self.collision_layer = 0x1  # Default layer
        
    def get_rect(self):
        """Get collision rectangle.
        
        Returns:
            pygame.Rect: Collision rectangle
        """
        from pygame import Rect
        transform = self.entity.get_component("TransformComponent")
        if not transform:
            return None
            
        return Rect(
            transform.x + self.offset_x,
            transform.y + self.offset_y,
            self.width,
            self.height
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "width": self.width,
            "height": self.height,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "is_trigger": self.is_trigger,
            "collision_mask": self.collision_mask,
            "collision_layer": self.collision_layer
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], entity: 'Entity') -> 'CollisionComponent':
        """Create component from dictionary."""
        component = cls(
            entity=entity,
            width=data.get("width", 32.0),
            height=data.get("height", 32.0)
        )
        component.offset_x = data.get("offset_x", 0.0)
        component.offset_y = data.get("offset_y", 0.0)
        component.is_trigger = data.get("is_trigger", False)
        component.collision_mask = data.get("collision_mask", 0xFFFFFFFF)
        component.collision_layer = data.get("collision_layer", 0x1)
        return component 