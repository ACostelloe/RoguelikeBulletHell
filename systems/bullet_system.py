from typing import List, Optional
from entities import EntityType
from components import TransformComponent, VelocityComponent, LifetimeComponent

class BulletSystem:
    """System for processing bullet entities."""
    
    def __init__(self, entity_manager):
        """Initialize the bullet system."""
        self.entity_manager = entity_manager

    def update(self, delta_time: float):
        """Update all bullet entities."""
        for entity in self.entity_manager.get_entities_by_type(EntityType.BULLET):
            # Get required components
            transform = entity.get_component(TransformComponent)
            velocity = entity.get_component(VelocityComponent)
            lifetime = entity.get_component(LifetimeComponent)

            # Update position if both transform and velocity exist
            if transform and velocity:
                transform.x += velocity.vx * delta_time
                transform.y += velocity.vy * delta_time

            # Check lifetime and remove if expired
            if lifetime:
                lifetime.frames_left -= 1
                if lifetime.frames_left <= 0:
                    self.entity_manager.remove_entity(entity.id) 