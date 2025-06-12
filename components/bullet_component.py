"""
Bullet component for bullet/projectile entities.
"""
from typing import Dict, Any, TYPE_CHECKING
from base import Component

if TYPE_CHECKING:
    from entities import Entity

class BulletComponent(Component):
    """Component for bullet/projectile behavior."""
    def __init__(self, entity: 'Entity', speed: float = 0.0, direction: float = 0.0, damage: float = 0.0, lifespan: float = 2.0):
        """Initialize bullet component.
        Args:
            entity: The entity this component belongs to
            speed: Speed of the bullet
            direction: Direction in radians
            damage: Damage dealt by the bullet
            lifespan: Time in seconds before bullet expires
        """
        super().__init__(entity)
        self.speed = speed
        self.direction = direction
        self.damage = damage
        self.lifespan = lifespan
        self.age = 0.0
        self.active = True

    def update(self, dt: float):
        self.age += dt
        if self.age >= self.lifespan:
            self.active = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "speed": self.speed,
            "direction": self.direction,
            "damage": self.damage,
            "lifespan": self.lifespan,
            "age": self.age,
            "active": self.active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], entity: 'Entity') -> 'BulletComponent':
        component = cls(
            entity=entity,
            speed=data.get("speed", 0.0),
            direction=data.get("direction", 0.0),
            damage=data.get("damage", 0.0),
            lifespan=data.get("lifespan", 2.0)
        )
        component.age = data.get("age", 0.0)
        component.active = data.get("active", True)
        return component 