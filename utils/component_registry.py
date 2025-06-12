"""
Component registry for managing component types.
"""
from typing import Dict, Type, Any
from base import Component

class ComponentRegistry:
    """Registry for component types."""
    
    _instance = None
    _components: Dict[str, Type[Component]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ComponentRegistry, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, component_type: Type[Component]) -> None:
        """Register a component type."""
        cls._components[component_type.__name__] = component_type
    
    @classmethod
    def get(cls, name: str) -> Type[Component]:
        """Get a component type by name."""
        return cls._components.get(name)
    
    @classmethod
    def get_all(cls) -> Dict[str, Type[Component]]:
        """Get all registered component types."""
        return cls._components.copy()
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered component types."""
        cls._components.clear() 