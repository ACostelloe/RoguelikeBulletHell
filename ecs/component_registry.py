from typing import Dict, Type, List
from entities import Component

class ComponentRegistry:
    """Registry for all component types in the ECS system."""
    
    # Core components
    ALL_COMPONENTS = [
        'Transform', 'Sprite', 'UI', 'Particle', 'Health', 
        'StatusEffect', 'Loot', 'Powerup', 'Physics', 'Collision',
        'Audio', 'Config', 'State', 'PlayerStats'
    ]

    # Component type mapping
    COMPONENT_TYPES: Dict[str, Type[Component]] = {}

    @classmethod
    def register_component(cls, name: str, component_type: Type[Component]) -> None:
        """Register a component type."""
        cls.COMPONENT_TYPES[name] = component_type

    @classmethod
    def get_component_type(cls, name: str) -> Type[Component]:
        """Get a component type by name."""
        return cls.COMPONENT_TYPES.get(name)

    @classmethod
    def is_valid_component(cls, name: str) -> bool:
        """Check if a component name is valid."""
        return name in cls.ALL_COMPONENTS

    @classmethod
    def get_all_component_types(cls) -> List[Type[Component]]:
        """Get all registered component types."""
        return list(cls.COMPONENT_TYPES.values()) 