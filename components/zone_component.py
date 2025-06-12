"""
Zone component for entity zone management.
"""
from typing import Dict, Any, TYPE_CHECKING
from base import Component

if TYPE_CHECKING:
    from entities import Entity

class ZoneComponent(Component):
    """Component for entity zone management."""
    def __init__(self, entity: 'Entity', zone_id: str = None):
        """Initialize zone component.
        
        Args:
            entity: The entity this component belongs to
            zone_id: Unique identifier for the zone
        """
        super().__init__(entity)
        self.zone_id = zone_id
        self.is_active = True
        self.triggered = False
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "zone_id": self.zone_id,
            "is_active": self.is_active,
            "triggered": self.triggered
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], entity: 'Entity') -> 'ZoneComponent':
        """Create component from dictionary."""
        component = cls(
            entity=entity,
            zone_id=data.get("zone_id")
        )
        component.is_active = data.get("is_active", True)
        component.triggered = data.get("triggered", False)
        return component 