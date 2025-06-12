"""
State component for entity state management.
"""
from typing import Dict, Any, TYPE_CHECKING
import logging
from base import Component

if TYPE_CHECKING:
    from entities import Entity

class StateComponent(Component):
    """Component for entity state management."""
    def __init__(self, entity: 'Entity', initial_state="idle"):
        """Initialize state component.
        
        Args:
            entity: The entity this component belongs to
            initial_state: The initial state of the entity
        """
        super().__init__(entity)
        self.logger = logging.getLogger("StateComponent")
        self.current_state = initial_state
        self.previous_state = None
        self.state_time = 0.0
        
    @property
    def state(self):
        return self.current_state

    @state.setter
    def state(self, value):
        self.current_state = value
        
    def change_state(self, new_state: str) -> None:
        """Change entity state.
        
        Args:
            new_state: New state to transition to
        """
        if new_state == self.current_state:
            return
            
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_time = 0.0
        self.logger.debug(f"Entity {self.entity.id} changed state from {self.previous_state} to {new_state}")
        
    def update(self, dt: float) -> None:
        """Update state component.
        
        Args:
            dt: Delta time in seconds
        """
        self.state_time += dt
        
    def render(self, surface) -> None:
        """Render state-specific visuals.
        
        Args:
            surface: Surface to render on
        """
        pass  # Override in subclasses if needed
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "current_state": self.current_state,
            "previous_state": self.previous_state,
            "state_time": self.state_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], entity: 'Entity') -> 'StateComponent':
        """Create component from dictionary."""
        component = cls(entity)
        component.current_state = data.get("current_state", "idle")
        component.previous_state = data.get("previous_state")
        component.state_time = data.get("state_time", 0.0)
        return component

    def set_state(self, new_state):
        self.current_state = new_state 