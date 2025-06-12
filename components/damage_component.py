"""
Damage component for entity damage management.
"""
from typing import Dict, Any, TYPE_CHECKING
from base import Component

if TYPE_CHECKING:
    from entities import Entity

class DamageComponent(Component):
    """Component for entity damage management."""
    def __init__(self, entity: 'Entity', damage: float = 0.0):
        """Initialize damage component.
        
        Args:
            entity: The entity this component belongs to
            damage: Base damage value
        """
        super().__init__(entity)
        self.damage = damage
        self.damage_multiplier = 1.0
        self.critical_chance = 0.0
        self.critical_multiplier = 2.0
        
    def get_damage(self) -> float:
        """Calculate final damage value."""
        return self.damage * self.damage_multiplier
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "damage": self.damage,
            "damage_multiplier": self.damage_multiplier,
            "critical_chance": self.critical_chance,
            "critical_multiplier": self.critical_multiplier
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], entity: 'Entity') -> 'DamageComponent':
        """Create component from dictionary."""
        component = cls(
            entity=entity,
            damage=data.get("damage", 0.0)
        )
        component.damage_multiplier = data.get("damage_multiplier", 1.0)
        component.critical_chance = data.get("critical_chance", 0.0)
        component.critical_multiplier = data.get("critical_multiplier", 2.0)
        return component 