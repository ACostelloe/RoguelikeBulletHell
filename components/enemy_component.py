"""
Enemy component for enemy-specific properties and behavior.
"""
from typing import Dict, Any, TYPE_CHECKING
from base import Component

if TYPE_CHECKING:
    from entities import Entity

class EnemyComponent(Component):
    """Component for enemy-specific properties and behavior."""
    def __init__(self, entity: 'Entity', enemy_type: str = "basic", ai_type: str = "default", level: int = 1):
        """Initialize enemy component.
        Args:
            entity: The entity this component belongs to
            enemy_type: Type of enemy (e.g., 'basic', 'elite', 'boss')
            ai_type: AI behavior type
            level: Enemy level
        """
        super().__init__(entity)
        self.enemy_type = enemy_type
        self.ai_type = ai_type
        self.level = level
        self.is_boss = enemy_type.lower() == "boss"
        self.spawn_time = 0.0
        self.aggro = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enemy_type": self.enemy_type,
            "ai_type": self.ai_type,
            "level": self.level,
            "is_boss": self.is_boss,
            "spawn_time": self.spawn_time,
            "aggro": self.aggro
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], entity: 'Entity') -> 'EnemyComponent':
        component = cls(
            entity=entity,
            enemy_type=data.get("enemy_type", "basic"),
            ai_type=data.get("ai_type", "default"),
            level=data.get("level", 1)
        )
        component.is_boss = data.get("is_boss", False)
        component.spawn_time = data.get("spawn_time", 0.0)
        component.aggro = data.get("aggro", False)
        return component 