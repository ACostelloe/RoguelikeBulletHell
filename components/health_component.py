"""
Health component for entity health and damage handling.
"""
from typing import Dict, Any, TYPE_CHECKING
import logging
from base import Component

if TYPE_CHECKING:
    from entities import Entity

class HealthComponent(Component):
    """Component for entity health."""
    def __init__(self, entity: 'Entity', max_health: float = 100.0):
        """Initialize health component.
        
        Args:
            entity: The entity this component belongs to
            max_health: Maximum health value
        """
        super().__init__(entity)
        self.logger = logging.getLogger("HealthComponent")
        
        self.entity = entity
        self.max_health = max_health
        self.current_health = max_health
        self.invincible = False
        self.invincible_timer = 0.0
        self.invincible_duration = 0.0
        
    def update(self, dt: float) -> None:
        """Update health component.
        
        Args:
            dt: Delta time in seconds
        """
        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False
                self.logger.debug(f"Entity {self.entity.id} is no longer invincible")
    
    def take_damage(self, amount: float) -> bool:
        """Take damage.
        
        Args:
            amount: Amount of damage to take
            
        Returns:
            bool: True if damage was taken, False if invincible
        """
        if self.invincible:
            self.logger.debug(f"Entity {self.entity.id} is invincible, no damage taken")
            return False
            
        self.current_health = max(0, self.current_health - amount)
        self.logger.debug(f"Entity {self.entity.id} took {amount} damage, health: {self.current_health}")
        
        if self.is_dead():
            self.logger.info(f"Entity {self.entity.id} died")
            
        return True
    
    def heal(self, amount: float) -> bool:
        """Heal the entity.
        
        Args:
            amount: Amount of health to restore
            
        Returns:
            bool: True if healing was applied
        """
        if self.is_dead():
            self.logger.warning(f"Cannot heal dead entity {self.entity.id}")
            return False
            
        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        
        if self.current_health > old_health:
            self.logger.debug(f"Entity {self.entity.id} healed for {amount}, health: {self.current_health}")
            return True
            
        return False
    
    def is_dead(self) -> bool:
        """Check if entity is dead.
        
        Returns:
            bool: True if entity is dead
        """
        return self.current_health <= 0
    
    def set_invincible(self, duration: float) -> None:
        """Set entity as invincible for a duration.
        
        Args:
            duration: Duration of invincibility in seconds
        """
        self.invincible = True
        self.invincible_timer = duration
        self.invincible_duration = duration
        self.logger.debug(f"Entity {self.entity.id} is invincible for {duration} seconds")
    
    def get_health_percentage(self) -> float:
        """Get current health as a percentage.
        
        Returns:
            float: Health percentage (0.0 to 1.0)
        """
        return self.current_health / self.max_health
    
    def reset(self) -> None:
        """Reset health to maximum."""
        self.current_health = self.max_health
        self.invincible = False
        self.invincible_timer = 0.0
        self.logger.debug(f"Entity {self.entity.id} health reset to {self.max_health}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "max_health": self.max_health,
            "current_health": self.current_health,
            "invincible": self.invincible,
            "invincible_timer": self.invincible_timer,
            "invincible_duration": self.invincible_duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], entity: 'Entity') -> 'HealthComponent':
        """Create component from dictionary."""
        component = cls(
            entity=entity,
            max_health=data.get("max_health", 100.0)
        )
        component.current_health = data.get("current_health", component.max_health)
        component.invincible = data.get("invincible", False)
        component.invincible_timer = data.get("invincible_timer", 0.0)
        component.invincible_duration = data.get("invincible_duration", 0.0)
        return component 