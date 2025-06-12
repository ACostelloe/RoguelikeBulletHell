from typing import Dict, List, Optional
from entities import EntityType
from components import TransformComponent, CollisionComponent, HealthComponent, EnemyComponent, LootComponent

class ZoneEntitySpawner:
    """System for spawning entities in zones."""
    
    def __init__(self, entity_manager):
        """Initialize the zone entity spawner."""
        self.entity_manager = entity_manager

    def update(self, delta_time: float):
        """Update the zone entity spawner."""
        # Currently no per-frame updates needed
        pass

    def spawn_zone_entities(self, zone_template):
        """Spawn all entities defined in a zone template."""
        # Spawn Enemies
        for enemy_data in zone_template.enemies:
            entity = self.entity_manager.create_entity(EntityType.ENEMY)
            
            # Add transform component
            transform = TransformComponent(entity)
            transform.x = enemy_data.x
            transform.y = enemy_data.y
            entity.add_component(transform)
            
            # Add enemy-specific components
            entity.add_component(EnemyComponent(entity, enemy_type=enemy_data.type))
            entity.add_component(HealthComponent(entity, health=enemy_data.health))
            
            # Add collision component
            collision = CollisionComponent(entity)
            collision.width = 32
            collision.height = 32
            entity.add_component(collision)

            self.entity_manager.add_entity(entity)

        # Spawn Loot
        for loot_data in zone_template.loot:
            entity = self.entity_manager.create_entity(EntityType.LOOT)
            
            # Add transform component
            transform = TransformComponent(entity)
            transform.x = loot_data.x
            transform.y = loot_data.y
            entity.add_component(transform)
            
            # Add loot-specific components
            entity.add_component(LootComponent(loot_type=loot_data.type))
            
            # Add collision component
            collision = CollisionComponent(entity)
            collision.width = 16
            collision.height = 16
            entity.add_component(collision)

            self.entity_manager.add_entity(entity)

        # Spawn Decorations (if needed)
        for decor_data in getattr(zone_template, 'decorations', []):
            entity = self.entity_manager.create_entity(EntityType.DECORATION)
            
            # Add transform component
            transform = TransformComponent(entity)
            transform.x = decor_data.x
            transform.y = decor_data.y
            entity.add_component(transform)
            
            # Add decoration-specific components as needed 
            self.entity_manager.add_entity(entity) 