"""
Physics system for handling game physics.
"""
from typing import List
from entities import Entity

class PhysicsSystem:
    """Handles physics calculations and updates."""
    
    def __init__(self):
        """Initialize the physics system."""
        self.entities: List[Entity] = []
    
    def add_entity(self, entity: Entity):
        """Add an entity to the physics system."""
        self.entities.append(entity)
    
    def remove_entity(self, entity: Entity):
        """Remove an entity from the physics system."""
        if entity in self.entities:
            self.entities.remove(entity)
    
    def update(self, delta_time: float):
        """Update physics for all entities."""
        for entity in self.entities:
            # Update entity physics here
            pass 