"""
Transform component for entity position, rotation, and scale.
"""
from typing import Dict, Any, Tuple, TYPE_CHECKING
from dataclasses import dataclass
from base import Component

if TYPE_CHECKING:
    from entities import Entity

@dataclass
class TransformComponent(Component):
    """Component for entity transform properties."""
    entity: 'Entity'
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0

    def get_position(self) -> Tuple[float, float]:
        """Get the current position as a tuple."""
        return (self.x, self.y)

    def set_position(self, x: float, y: float) -> None:
        """Set the position."""
        self.x = x
        self.y = y

    def move(self, dx: float, dy: float) -> None:
        """Move the entity by the given delta."""
        self.x += dx
        self.y += dy

    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "x": self.x,
            "y": self.y,
            "rotation": self.rotation,
            "scale_x": self.scale_x,
            "scale_y": self.scale_y
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], entity: 'Entity') -> 'TransformComponent':
        """Create component from dictionary."""
        return cls(
            entity=entity,
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            rotation=data.get("rotation", 0.0),
            scale_x=data.get("scale_x", 1.0),
            scale_y=data.get("scale_y", 1.0)
        ) 