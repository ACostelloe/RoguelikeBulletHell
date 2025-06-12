"""
Collision detection and response system.
"""
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
import pygame
from entities import Entity, Component
from logger import logger
import traceback

@dataclass
class CollisionComponent(Component):
    """Component for handling collisions."""
    width: float
    height: float
    offset_x: float = 0.0
    offset_y: float = 0.0
    is_trigger: bool = False
    collision_mask: int = 0xFFFFFFFF
    collision_layer: int = 0x00000001
    
    def get_rect(self, entity: Entity) -> pygame.Rect:
        """Get the collision rectangle for an entity."""
        transform = entity.get_component(TransformComponent)
        if not transform:
            logger.warning(f"Entity {entity.id} missing TransformComponent for collision rect")
            return pygame.Rect(0, 0, 0, 0)
            
        return pygame.Rect(
            transform.x + self.offset_x,
            transform.y + self.offset_y,
            self.width,
            self.height
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "width": self.width,
            "height": self.height,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "is_trigger": self.is_trigger,
            "collision_mask": self.collision_mask,
            "collision_layer": self.collision_layer
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CollisionComponent':
        """Create component from dictionary."""
        return cls(
            width=data["width"],
            height=data["height"],
            offset_x=data["offset_x"],
            offset_y=data["offset_y"],
            is_trigger=data["is_trigger"],
            collision_mask=data["collision_mask"],
            collision_layer=data["collision_layer"]
        )

class CollisionManager:
    """Manages collision detection and response."""
    
    def __init__(self):
        """Initialize the collision manager."""
        self.spatial_hash: Dict[Tuple[int, int], Set[str]] = {}
        self.cell_size: int = 64  # Size of spatial hash cells
        self.collision_count: int = 0
        self.trigger_count: int = 0
        logger.info("Initialized CollisionManager")
        
    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        """Get the cell coordinates for a position."""
        return (int(x // self.cell_size), int(y // self.cell_size))
        
    def _get_cells_for_rect(self, rect: pygame.Rect) -> List[Tuple[int, int]]:
        """Get all cells that a rectangle overlaps."""
        start_x = int(rect.left // self.cell_size)
        start_y = int(rect.top // self.cell_size)
        end_x = int(rect.right // self.cell_size)
        end_y = int(rect.bottom // self.cell_size)
        
        cells = []
        for x in range(start_x, end_x + 1):
            for y in range(start_y, end_y + 1):
                cells.append((x, y))
        return cells
        
    def add_entity(self, entity_id: str, entity: Entity) -> None:
        """Add an entity to the spatial hash."""
        collision = entity.get_component(CollisionComponent)
        if not collision:
            logger.warning(f"Entity {entity_id} missing CollisionComponent")
            return
            
        rect = collision.get_rect(entity)
        cells = self._get_cells_for_rect(rect)
        
        for cell in cells:
            if cell not in self.spatial_hash:
                self.spatial_hash[cell] = set()
            self.spatial_hash[cell].add(entity_id)
            
        logger.debug(f"Registered collision for entity {entity_id} in cells {cells}")
            
    def remove_entity(self, entity_id: str, entity: Entity) -> None:
        """Remove an entity from the spatial hash."""
        collision = entity.get_component(CollisionComponent)
        if not collision:
            return
            
        rect = collision.get_rect(entity)
        cells = self._get_cells_for_rect(rect)
        
        for cell in cells:
            if cell in self.spatial_hash:
                self.spatial_hash[cell].discard(entity_id)
                if not self.spatial_hash[cell]:
                    del self.spatial_hash[cell]
                    
        logger.debug(f"Removed collision for entity {entity_id} from cells {cells}")
                    
    def update_entity(self, entity_id: str, entity: Entity) -> None:
        """Update an entity's position in the spatial hash."""
        self.remove_entity(entity_id, entity)
        self.add_entity(entity_id, entity)
        
    def get_potential_collisions(self, entity_id: str, entity: Entity) -> Set[str]:
        """Get all entities that could collide with the given entity."""
        collision = entity.get_component(CollisionComponent)
        if not collision:
            return set()
            
        rect = collision.get_rect(entity)
        cells = self._get_cells_for_rect(rect)
        
        potential_collisions = set()
        for cell in cells:
            if cell in self.spatial_hash:
                potential_collisions.update(self.spatial_hash[cell])
                
        potential_collisions.discard(entity_id)
        return potential_collisions
        
    def check_collision(self, entity1: Entity, entity2: Entity) -> bool:
        """Check if two entities are colliding."""
        collision1 = entity1.get_component(CollisionComponent)
        collision2 = entity2.get_component(CollisionComponent)
        
        if not collision1 or not collision2:
            return False
            
        # Check collision masks
        if not (collision1.collision_layer & collision2.collision_mask) and \
           not (collision2.collision_layer & collision1.collision_mask):
            return False
            
        rect1 = collision1.get_rect(entity1)
        rect2 = collision2.get_rect(entity2)
        
        is_colliding = rect1.colliderect(rect2)
        if is_colliding:
            logger.debug(f"Collision detected between {entity1.id} and {entity2.id}")
            
        return is_colliding
        
    def handle_collision(self, entity1: Entity, entity2: Entity) -> None:
        """Handle collision between two entities."""
        try:
            collision1 = entity1.get_component(CollisionComponent)
            collision2 = entity2.get_component(CollisionComponent)
            
            if not collision1 or not collision2:
                return
                
            # Handle trigger collisions
            if collision1.is_trigger or collision2.is_trigger:
                self.trigger_count += 1
                logger.debug(f"Trigger collision between {entity1.id} and {entity2.id}")
                entity1.on_trigger_enter(entity2)
                entity2.on_trigger_enter(entity1)
                return
                
            # Handle physical collisions
            self.collision_count += 1
            rect1 = collision1.get_rect(entity1)
            rect2 = collision2.get_rect(entity2)
            
            # Calculate collision response
            overlap_x = min(rect1.right, rect2.right) - max(rect1.left, rect2.left)
            overlap_y = min(rect1.bottom, rect2.bottom) - max(rect1.top, rect2.top)
            
            if overlap_x < overlap_y:
                # Horizontal collision
                if rect1.centerx < rect2.centerx:
                    logger.debug(f"Horizontal collision: {entity1.id} right -> {entity2.id} left")
                    entity1.on_collision(entity2, "right")
                    entity2.on_collision(entity1, "left")
                else:
                    logger.debug(f"Horizontal collision: {entity1.id} left -> {entity2.id} right")
                    entity1.on_collision(entity2, "left")
                    entity2.on_collision(entity1, "right")
            else:
                # Vertical collision
                if rect1.centery < rect2.centery:
                    logger.debug(f"Vertical collision: {entity1.id} bottom -> {entity2.id} top")
                    entity1.on_collision(entity2, "bottom")
                    entity2.on_collision(entity1, "top")
                else:
                    logger.debug(f"Vertical collision: {entity1.id} top -> {entity2.id} bottom")
                    entity1.on_collision(entity2, "top")
                    entity2.on_collision(entity1, "bottom")
                    
        except Exception as e:
            logger.error(f"Error handling collision between {entity1.id} and {entity2.id}: {str(e)}")
            logger.error(traceback.format_exc())
            
    def update(self, entity_manager) -> None:
        """Update all collisions."""
        try:
            # Reset collision counters
            self.collision_count = 0
            self.trigger_count = 0
            
            # Clear spatial hash
            self.spatial_hash.clear()
            
            # Rebuild spatial hash
            for entity_id, entity in entity_manager.entities.items():
                if entity.active:
                    self.add_entity(entity_id, entity)
                    
            # Check collisions
            for entity_id, entity in entity_manager.entities.items():
                if not entity.active:
                    continue
                    
                potential_collisions = self.get_potential_collisions(entity_id, entity)
                
                for other_id in potential_collisions:
                    other = entity_manager.get_entity(other_id)
                    if other and other.active and self.check_collision(entity, other):
                        self.handle_collision(entity, other)
                        
            # Log collision statistics
            logger.debug(f"Collision update: {self.collision_count} physical collisions, {self.trigger_count} trigger collisions")
                        
        except Exception as e:
            logger.error(f"Error updating collisions: {str(e)}")
            logger.error(traceback.format_exc())
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert manager to dictionary."""
        return {
            "cell_size": self.cell_size,
            "spatial_hash": {
                f"{x},{y}": list(entities)
                for (x, y), entities in self.spatial_hash.items()
            }
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CollisionManager':
        """Create manager from dictionary."""
        manager = cls()
        manager.cell_size = data["cell_size"]
        
        for cell_str, entities in data["spatial_hash"].items():
            x, y = map(int, cell_str.split(","))
            manager.spatial_hash[(x, y)] = set(entities)
            
        return manager 