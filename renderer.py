"""
Rendering system.
"""
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
import pygame
from entities import Entity, Component, TransformComponent
from components import SpriteComponent
from logger import logger
import traceback

class Renderer:
    """Manages rendering."""
    
    def __init__(self, screen, entity_manager, asset_manager):
        """Initialize the renderer."""
        self.screen = screen
        self.entity_manager = entity_manager
        self.asset_manager = asset_manager
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.0
        self.layers: Dict[int, List[Tuple[Entity, SpriteComponent]]] = {}
        self.debug_overlay_enabled = False
        self.debug_font = pygame.font.Font(None, 16)
        self.view_frustum = pygame.Rect(0, 0, self.width, self.height)
        
    def set_camera(self, x: float, y: float) -> None:
        """Set the camera position."""
        self.camera_x = x
        self.camera_y = y
        
    def set_zoom(self, zoom: float) -> None:
        """Set the camera zoom."""
        self.zoom = max(0.1, min(zoom, 10.0))
        
    def world_to_screen(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates."""
        screen_x = int((x - self.camera_x) * self.zoom + self.width / 2)
        screen_y = int((y - self.camera_y) * self.zoom + self.height / 2)
        return screen_x, screen_y
        
    def screen_to_world(self, x: int, y: int) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        world_x = (x - self.width / 2) / self.zoom + self.camera_x
        world_y = (y - self.height / 2) / self.zoom + self.camera_y
        return world_x, world_y
        
    def is_visible(self, rect: pygame.Rect) -> bool:
        """Check if a rectangle is visible on screen."""
        screen_rect = pygame.Rect(
            *self.world_to_screen(rect.left, rect.top),
            rect.width * self.zoom,
            rect.height * self.zoom
        )
        return screen_rect.colliderect(self.screen.get_rect())
        
    def is_in_view(self, x: float, y: float, width: float = 0, height: float = 0) -> bool:
        """Check if a point or rectangle is within the camera's view frustum."""
        screen_x = int((x - self.camera_x) * self.zoom + self.width / 2)
        screen_y = int((y - self.camera_y) * self.zoom + self.height / 2)
        
        if width == 0 and height == 0:
            # Point check
            return (0 <= screen_x < self.width and 
                   0 <= screen_y < self.height)
        
        # Rectangle check
        screen_rect = pygame.Rect(screen_x, screen_y, width * self.zoom, height * self.zoom)
        return screen_rect.colliderect(self.screen.get_rect())
        
    def render_entity(self, entity: Entity, sprite: SpriteComponent) -> None:
        """Render an entity's sprite."""
        try:
            if not sprite.visible:
                return
            if sprite.image is None:
                return
                
            # Get entity position
            transform = entity.get_component(TransformComponent)
            if not transform:
                return
                
            # Calculate screen position
            screen_x, screen_y = self.world_to_screen(
                transform.x + sprite.offset_x,
                transform.y + sprite.offset_y
            )
            
            # Scale and rotate sprite
            scaled_size = (
                int(sprite.image.get_width() * sprite.scale * self.zoom),
                int(sprite.image.get_height() * sprite.scale * self.zoom)
            )
            scaled_sprite = pygame.transform.scale(sprite.image, scaled_size)
            
            if sprite.rotation != 0:
                scaled_sprite = pygame.transform.rotate(scaled_sprite, sprite.rotation)
                
            if sprite.flip_x or sprite.flip_y:
                scaled_sprite = pygame.transform.flip(
                    scaled_sprite,
                    sprite.flip_x,
                    sprite.flip_y
                )
                
            # Set alpha
            if sprite.alpha != 255:
                scaled_sprite.set_alpha(sprite.alpha)
                
            # Draw sprite
            self.screen.blit(
                scaled_sprite,
                (screen_x - scaled_sprite.get_width() / 2,
                 screen_y - scaled_sprite.get_height() / 2)
            )
            
        except Exception as e:
            logger.error(f"Error rendering entity: {str(e)}")
            logger.error(traceback.format_exc())
            
    def update(self, entity_manager) -> None:
        """Update rendering."""
        try:
            # Clear screen
            self.screen.fill((0, 0, 0))
            
            # Sort entities by layer
            self.layers.clear()
            for entity_id, entity in entity_manager.entities.items():
                if not entity.active:
                    continue
                    
                sprite = entity.get_component(SpriteComponent)
                if not sprite:
                    continue
                    
                if sprite.layer not in self.layers:
                    self.layers[sprite.layer] = []
                self.layers[sprite.layer].append((entity, sprite))
                
            # Render each layer
            for layer in sorted(self.layers.keys()):
                for entity, sprite in self.layers[layer]:
                    self.render_entity(entity, sprite)
                    
            # Update display
            pygame.display.flip()
            
        except Exception as e:
            logger.error(f"Error updating renderer: {str(e)}")
            logger.error(traceback.format_exc())
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert renderer to dictionary."""
        return {
            "width": self.width,
            "height": self.height,
            "camera_x": self.camera_x,
            "camera_y": self.camera_y,
            "zoom": self.zoom
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Renderer':
        """Create renderer from dictionary."""
        renderer = cls(data["width"], data["height"])
        renderer.camera_x = data["camera_x"]
        renderer.camera_y = data["camera_y"]
        renderer.zoom = data["zoom"]
        return renderer

    def toggle_debug_overlay(self):
        """Toggle the debug overlay."""
        self.debug_overlay_enabled = not self.debug_overlay_enabled
        logger.info(f"Debug overlay {'enabled' if self.debug_overlay_enabled else 'disabled'}")
        
    def render_background(self, screen: pygame.Surface, camera: 'Camera') -> None:
        """Render the background with parallax effect."""
        try:
            background = self.asset_manager.get_image("background")
            if background:
                # Get screen dimensions
                screen_width, screen_height = screen.get_size()
                
                # Calculate how many tiles we need to cover the screen
                tile_width = 32  # Assuming each tile is 32x32 pixels
                tile_height = 32
                tiles_x = (screen_width // tile_width) + 2  # +2 for safety
                tiles_y = (screen_height // tile_height) + 2
                
                # Calculate camera offset for parallax effect
                offset_x = int(camera.x * 0.5) % tile_width  # Slower parallax for background
                offset_y = int(camera.y * 0.5) % tile_height
                
                # Draw background tiles
                for y in range(tiles_y):
                    for x in range(tiles_x):
                        # Calculate screen position
                        screen_x = (x * tile_width) - offset_x
                        screen_y = (y * tile_height) - offset_y
                        
                        # Draw the tile
                        screen.blit(background, (screen_x, screen_y))
        except Exception as e:
            print(f"[RENDER ERROR] Failed to render background: {e}")

    def render(self, screen: pygame.Surface, entities: List['Entity'], camera: 'Camera') -> None:
        """Render all entities and the background."""
        print("[RENDER] Entering render method")
        
        # Clear the screen
        screen.fill((0, 0, 0))  # Black background
        
        # Render background tiles
        if self.asset_manager.tiles:
            # Calculate how many tiles we need to cover the screen
            tile_size = 32
            tiles_x = (screen.get_width() // tile_size) + 2  # +2 for safety
            tiles_y = (screen.get_height() // tile_size) + 2
            
            # Calculate camera offset for parallax effect
            offset_x = int(camera.x * 0.5) % tile_size  # Slower parallax for background
            offset_y = int(camera.y * 0.5) % tile_size
            
            # Draw background tiles
            for y in range(tiles_y):
                for x in range(tiles_x):
                    # Calculate screen position
                    screen_x = (x * tile_size) - offset_x
                    screen_y = (y * tile_size) - offset_y
                    
                    # Get and draw the tile (using grass biome for now)
                    tile = self.asset_manager.tiles.get_tile('grass', 0)
                    screen.blit(tile, (screen_x, screen_y))
        
        # Update camera position
        self.camera_x = camera.x
        self.camera_y = camera.y
        self.camera_zoom = camera.zoom

        # Render all entities
        print(f"[RENDER] Total entities to render: {len(entities)}")
        for entity in entities:
            try:
                sprite = entity.get_component(SpriteComponent)
                self.render_entity(entity, sprite)
            except Exception as e:
                print(f"[RENDER ERROR] Failed to render entity: {e}")
                import traceback
                print(traceback.format_exc())
        
        # Update display
        pygame.display.flip()
        
    def render_all(self, surface, camera, world_manager, entity_manager, bullet_manager, enemy_manager, ui_manager):
        """Render everything in the correct order."""
        try:
            # Clear screen
            surface.fill((0, 0, 0))
            
            # Get camera position
            if hasattr(camera, 'get_component'):
                transform = camera.get_component(TransformComponent)
                camera_x = transform.x if transform else 0
                camera_y = transform.y if transform else 0
            else:
                camera_x = getattr(camera, 'x', 0)
                camera_y = getattr(camera, 'y', 0)
            
            # Render world
            zone = world_manager.active_zone
            if zone:
                for tile in zone.tiles:
                    if tile.sprite:
                        surface.blit(tile.sprite, camera.apply(tile.rect))
                    else:
                        # Optional fallback for missing sprites
                        pygame.draw.rect(surface, (255, 0, 0), camera.apply(tile.rect))
            
            # Render chunks
            if hasattr(world_manager, 'chunk_manager'):
                world_manager.chunk_manager.draw(surface)
            
            # Render entities
            for entity_id, entity in entity_manager.entities.items():
                if not entity.active:
                    continue
                sprite = entity.get_component(SpriteComponent)
                if sprite:
                    self.render_entity(entity, sprite)
            
            # Render bullets
            if bullet_manager:
                bullet_manager.draw(surface, camera_x, camera_y)
            
            # Render UI
            if ui_manager:
                ui_manager.render(surface)
            
            # Update display
            pygame.display.flip()
            
        except Exception as e:
            logger.error(f"Error in render_all: {str(e)}")
            logger.error(traceback.format_exc())

    def render_world(self, surface, camera, world_manager):
        """Render the world tiles."""
        try:
            zone = world_manager.active_zone
            if not zone:
                return

            for tile in zone.tiles:
                if tile.sprite:
                    surface.blit(tile.sprite, camera.apply(tile.rect))
                else:
                    # Optional fallback for missing sprites
                    pygame.draw.rect(surface, (255, 0, 0), camera.apply(tile.rect))
        except Exception as e:
            logger.error(f"Error rendering world: {str(e)}")
            logger.error(traceback.format_exc())

    def render_entities(self, surface, entity_manager, camera):
        """Render all entities."""
        # Update camera position
        self.camera_x = camera.x
        self.camera_y = camera.y
        self.camera_zoom = camera.zoom

        # Render all entities
        for entity in entity_manager.get_all_entities():
            try:
                sprite = entity.get_component(SpriteComponent)
                if sprite:
                    self.render_entity(entity, sprite)
            except Exception as e:
                logger.error(f"Error rendering entity: {str(e)}")
                logger.error(traceback.format_exc())

    def clear(self):
        """Clear the screen."""
        self.screen.fill((0, 0, 0))  # Black background

    def present(self):
        """Present the rendered frame."""
        pygame.display.flip() 