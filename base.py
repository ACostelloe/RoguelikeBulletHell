"""
Base classes for the game.
"""
from typing import Dict, Any, TypeVar, Generic
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class Component:
    """Base class for entity components."""
    entity: 'Entity'
    
    def __init__(self, *args, **kwargs):
        self.callbacks = {}  # Ensure all components support callback storage
    
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