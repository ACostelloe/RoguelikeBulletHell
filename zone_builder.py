from tiles import TileFactory
from zone import Zone
from components import TransformComponent, SpriteComponent, ZoneComponent
from entities import Entity, EntityType
import logging
import traceback

logger = logging.getLogger(__name__)

class ZoneBuilder:
    def __init__(self, tile_factory, entity_manager):
        self.tile_factory = tile_factory
        self.entity_manager = entity_manager
        self.zone_size = 32  # Tile size

    def build_zone(self, template, x=0, y=0, zone_id=None):
        """Build a zone from a template with proper component binding."""
        try:
            zone_id = zone_id or template.name
            logger.info(f"Building zone {zone_id} at ({x}, {y})")
            
            # Create base zone
            zone = Zone(
                id=zone_id,
                template=template,
                x=x,
                y=y
            )
            
            # Create ECS entity for zone
            zone_entity = self.entity_manager.create_entity(EntityType.ZONE)
            
            # Add transform component
            transform = TransformComponent(zone_entity)
            transform.x = x * self.zone_size
            transform.y = y * self.zone_size
            zone_entity.add_component(transform)
            
            # Add zone component
            zone_component = ZoneComponent(zone_entity)
            zone_component.zone_type = template.zone_type
            zone_component.biome = template.biome
            zone_entity.add_component(zone_component)
            
            # Add sprite component for background
            sprite = SpriteComponent(zone_entity)
            sprite.image_key = f"background_{template.biome}"
            sprite.frame = 0
            zone_entity.add_component(sprite)
            
            # Register entity
            self.entity_manager.add_entity(zone_entity)
            
            logger.info(f"Successfully built zone {zone_id}")
            return zone
            
        except Exception as e:
            logger.error(f"Error building zone {zone_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise 