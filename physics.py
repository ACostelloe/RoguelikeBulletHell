"""
Physics system.
"""
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
import pygame
from entities import Entity, Component
from logger import logger
import traceback

@dataclass
class PhysicsComponent(Component):
    """Component for handling physics."""
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    acceleration_x: float = 0.0
    acceleration_y: float = 0.0
    max_speed: float = 0.0
    friction: float = 0.0
    gravity: float = 0.0
    mass: float = 1.0
    is_kinematic: bool = False
    is_static: bool = False
    
    def apply_force(self, force_x: float, force_y: float) -> None:
        """Apply a force to the entity."""
        if self.is_static:
            logger.debug(f"Attempted to apply force to static entity {self.entity.id}")
            return
            
        self.acceleration_x += force_x / self.mass
        self.acceleration_y += force_y / self.mass
        logger.debug(f"Applied force ({force_x}, {force_y}) to entity {self.entity.id}")
        
    def apply_impulse(self, impulse_x: float, impulse_y: float) -> None:
        """Apply an impulse to the entity."""
        if self.is_static:
            logger.debug(f"Attempted to apply impulse to static entity {self.entity.id}")
            return
            
        self.velocity_x += impulse_x / self.mass
        self.velocity_y += impulse_y / self.mass
        logger.debug(f"Applied impulse ({impulse_x}, {impulse_y}) to entity {self.entity.id}")
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "velocity_x": self.velocity_x,
            "velocity_y": self.velocity_y,
            "acceleration_x": self.acceleration_x,
            "acceleration_y": self.acceleration_y,
            "max_speed": self.max_speed,
            "friction": self.friction,
            "gravity": self.gravity,
            "mass": self.mass,
            "is_kinematic": self.is_kinematic,
            "is_static": self.is_static
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhysicsComponent':
        """Create component from dictionary."""
        return cls(
            velocity_x=data["velocity_x"],
            velocity_y=data["velocity_y"],
            acceleration_x=data["acceleration_x"],
            acceleration_y=data["acceleration_y"],
            max_speed=data["max_speed"],
            friction=data["friction"],
            gravity=data["gravity"],
            mass=data["mass"],
            is_kinematic=data["is_kinematic"],
            is_static=data["is_static"]
        )

class PhysicsManager:
    """Manages physics simulation."""
    
    def __init__(self):
        """Initialize the physics manager."""
        self.gravity: float = 980.0  # Pixels per second squared
        self.time_scale: float = 1.0
        self.entities: Dict[str, Tuple[Entity, PhysicsComponent]] = {}
        self.force_count: int = 0
        self.impulse_count: int = 0
        logger.info("Initialized PhysicsManager")
        
    def add_entity(self, entity_id: str, entity: Entity) -> None:
        """Add an entity to physics simulation."""
        physics = entity.get_component(PhysicsComponent)
        if physics:
            self.entities[entity_id] = (entity, physics)
            logger.debug(f"Added entity {entity_id} to physics simulation")
        else:
            logger.warning(f"Entity {entity_id} missing PhysicsComponent")
            
    def remove_entity(self, entity_id: str) -> None:
        """Remove an entity from physics simulation."""
        if entity_id in self.entities:
            self.entities.pop(entity_id)
            logger.debug(f"Removed entity {entity_id} from physics simulation")
        
    def update_entity(self, entity_id: str, entity: Entity) -> None:
        """Update an entity's physics component."""
        self.remove_entity(entity_id)
        self.add_entity(entity_id, entity)
        
    def apply_gravity(self, dt: float) -> None:
        """Apply gravity to all entities."""
        for entity_id, (entity, physics) in self.entities.items():
            if not physics.is_static and not physics.is_kinematic:
                physics.apply_force(0, physics.gravity * physics.mass * dt)
                logger.debug(f"Applied gravity to entity {entity_id}")
                
    def apply_friction(self, dt: float) -> None:
        """Apply friction to all entities."""
        for entity_id, (entity, physics) in self.entities.items():
            if not physics.is_static and not physics.is_kinematic:
                # Calculate friction force
                speed = (physics.velocity_x ** 2 + physics.velocity_y ** 2) ** 0.5
                if speed > 0:
                    friction_force = physics.friction * physics.mass * dt
                    friction_x = -physics.velocity_x / speed * friction_force
                    friction_y = -physics.velocity_y / speed * friction_force
                    physics.apply_force(friction_x, friction_y)
                    logger.debug(f"Applied friction to entity {entity_id}")
                    
    def update_velocities(self, dt: float) -> None:
        """Update velocities of all entities."""
        for entity_id, (entity, physics) in self.entities.items():
            if not physics.is_static and not physics.is_kinematic:
                # Update velocity
                physics.velocity_x += physics.acceleration_x * dt
                physics.velocity_y += physics.acceleration_y * dt
                
                # Apply max speed
                speed = (physics.velocity_x ** 2 + physics.velocity_y ** 2) ** 0.5
                if physics.max_speed > 0 and speed > physics.max_speed:
                    scale = physics.max_speed / speed
                    physics.velocity_x *= scale
                    physics.velocity_y *= scale
                    logger.debug(f"Limited speed of entity {entity_id} to {physics.max_speed}")
                    
                # Reset acceleration
                physics.acceleration_x = 0
                physics.acceleration_y = 0
                
    def update_positions(self, dt: float) -> None:
        """Update positions of all entities."""
        for entity_id, (entity, physics) in self.entities.items():
            if not physics.is_static:
                transform = entity.get_component(TransformComponent)
                if transform:
                    transform.x += physics.velocity_x * dt
                    transform.y += physics.velocity_y * dt
                    logger.debug(f"Updated position of entity {entity_id} to ({transform.x}, {transform.y})")
                else:
                    logger.warning(f"Entity {entity_id} missing TransformComponent")
                    
    def resolve_collisions(self, collision_manager) -> None:
        """Resolve collisions between entities."""
        for entity_id, (entity, physics) in self.entities.items():
            if physics.is_static:
                continue
                
            collision = entity.get_component(CollisionComponent)
            if not collision:
                continue
                
            # Get potential collisions
            potential_collisions = collision_manager.get_potential_collisions(entity_id, entity)
            
            for other_id in potential_collisions:
                other = collision_manager.get_entity(other_id)
                if not other:
                    continue
                    
                other_physics = other.get_component(PhysicsComponent)
                if not other_physics:
                    continue
                    
                # Check collision
                if collision_manager.check_collision(entity, other):
                    # Calculate collision response
                    self.resolve_collision(entity, physics, other, other_physics)
                    
    def resolve_collision(self, entity1: Entity, physics1: PhysicsComponent,
                         entity2: Entity, physics2: PhysicsComponent) -> None:
        """Resolve collision between two entities."""
        try:
            # Get collision components
            collision1 = entity1.get_component(CollisionComponent)
            collision2 = entity2.get_component(CollisionComponent)
            if not collision1 or not collision2:
                return
                
            # Get transform components
            transform1 = entity1.get_component(TransformComponent)
            transform2 = entity2.get_component(TransformComponent)
            if not transform1 or not transform2:
                return
                
            # Calculate collision normal
            rect1 = collision1.get_rect(entity1)
            rect2 = collision2.get_rect(entity2)
            
            overlap_x = min(rect1.right, rect2.right) - max(rect1.left, rect2.left)
            overlap_y = min(rect1.bottom, rect2.bottom) - max(rect1.top, rect2.top)
            
            if overlap_x < overlap_y:
                # Horizontal collision
                if rect1.centerx < rect2.centerx:
                    normal_x = -1
                    normal_y = 0
                else:
                    normal_x = 1
                    normal_y = 0
            else:
                # Vertical collision
                if rect1.centery < rect2.centery:
                    normal_x = 0
                    normal_y = -1
                else:
                    normal_x = 0
                    normal_y = 1
                    
            # Calculate relative velocity
            rel_vel_x = physics1.velocity_x - physics2.velocity_x
            rel_vel_y = physics1.velocity_y - physics2.velocity_y
            
            # Calculate impulse
            total_mass = physics1.mass + physics2.mass
            if total_mass == 0:
                return
                
            impulse = 2 * (rel_vel_x * normal_x + rel_vel_y * normal_y) / total_mass
            
            # Apply impulse
            if not physics1.is_static:
                physics1.velocity_x -= impulse * normal_x * physics2.mass
                physics1.velocity_y -= impulse * normal_y * physics2.mass
                logger.debug(f"Applied collision impulse to entity {entity1.id}")
                
            if not physics2.is_static:
                physics2.velocity_x += impulse * normal_x * physics1.mass
                physics2.velocity_y += impulse * normal_y * physics1.mass
                logger.debug(f"Applied collision impulse to entity {entity2.id}")
                
        except Exception as e:
            logger.error(f"Error resolving collision between {entity1.id} and {entity2.id}: {str(e)}")
            logger.error(traceback.format_exc())
            
    def update(self, dt: float, collision_manager) -> None:
        """Update physics simulation."""
        try:
            # Reset counters
            self.force_count = 0
            self.impulse_count = 0
            
            # Apply forces
            self.apply_gravity(dt)
            self.apply_friction(dt)
            
            # Update velocities
            self.update_velocities(dt)
            
            # Update positions
            self.update_positions(dt)
            
            # Resolve collisions
            self.resolve_collisions(collision_manager)
            
            # Log physics statistics
            logger.debug(f"Physics update: {self.force_count} forces applied, {self.impulse_count} impulses applied")
            
        except Exception as e:
            logger.error(f"Error updating physics: {str(e)}")
            logger.error(traceback.format_exc())
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert manager to dictionary."""
        return {
            "gravity": self.gravity,
            "time_scale": self.time_scale
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhysicsManager':
        """Create manager from dictionary."""
        manager = cls()
        manager.gravity = data["gravity"]
        manager.time_scale = data["time_scale"]
        return manager 