from typing import List, Dict, Type, Optional
from abc import ABC, abstractmethod
from entities import Entity, Component
from component_registry import ComponentRegistry

class System(ABC):
    """Base class for all ECS systems."""
    
    def __init__(self):
        self.required_components: List[str] = []
        self.optional_components: List[str] = []

    @abstractmethod
    def update(self, entities: List[Entity], delta_time: float) -> None:
        """Update all entities in this system."""
        raise NotImplementedError

    def filter_entities(self, entities: List[Entity]) -> List[Entity]:
        """Filter entities that have all required components."""
        return [
            entity for entity in entities
            if all(entity.has_component(comp) for comp in self.required_components)
        ]

class ParticleSystem(System):
    """System for updating particle effects."""
    
    def __init__(self):
        super().__init__()
        self.required_components = ['Particle']
        self.optional_components = ['Transform']

    def update(self, entities: List[Entity], delta_time: float) -> None:
        """Update all particle entities."""
        for entity in self.filter_entities(entities):
            particle = entity.get_component('Particle')
            if not particle:
                continue
                
            # Update particle lifetime
            particle.lifetime -= delta_time
            if particle.lifetime <= 0:
                entity.destroy()
                continue

            # Update particle position
            if entity.has_component('Transform'):
                transform = entity.get_component('Transform')
                transform.x += particle.velocity[0] * delta_time
                transform.y += particle.velocity[1] * delta_time

class PhysicsSystem(System):
    """System for updating physics."""
    
    def __init__(self):
        super().__init__()
        self.required_components = ['Physics', 'Transform']
        self.optional_components = ['Collision']

    def update(self, entities: List[Entity], delta_time: float) -> None:
        """Update all physics entities."""
        for entity in self.filter_entities(entities):
            physics = entity.get_component('Physics')
            transform = entity.get_component('Transform')
            if not physics or not transform:
                continue

            # Update velocity
            physics.velocity_x += physics.acceleration_x * delta_time
            physics.velocity_y += physics.acceleration_y * delta_time

            # Update position
            transform.x += physics.velocity_x * delta_time
            transform.y += physics.velocity_y * delta_time

class RenderSystem(System):
    """System for rendering entities."""
    
    def __init__(self):
        super().__init__()
        self.required_components = ['Transform']
        self.optional_components = ['Sprite', 'UI']

    def update(self, entities: List[Entity], delta_time: float) -> None:
        """Render all entities."""
        for entity in self.filter_entities(entities):
            transform = entity.get_component('Transform')
            if not transform:
                continue

            # Render sprite if present
            if entity.has_component('Sprite'):
                sprite = entity.get_component('Sprite')
                if sprite:
                    sprite.render(transform.x, transform.y)

            # Render UI if present
            if entity.has_component('UI'):
                ui = entity.get_component('UI')
                if ui and ui.visible:
                    ui.render(transform.x, transform.y) 