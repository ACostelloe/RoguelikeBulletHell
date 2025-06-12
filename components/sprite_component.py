"""
Sprite component for entity visual representation.
"""
from typing import Dict, List, Optional, Any, TYPE_CHECKING
import pygame
import logging
from base import Component

if TYPE_CHECKING:
    from entities import Entity

class SpriteComponent(Component):
    """Component for entity sprite."""
    def __init__(self, entity: 'Entity', image_key: str = None, visible: bool = True, 
                 offset_x: float = 0.0, offset_y: float = 0.0, frame: int = 0):
        """Initialize sprite component.
        
        Args:
            entity: The entity this component belongs to
            image_key: Key for the image in the asset manager
            visible: Whether the sprite is visible
            offset_x: X offset for sprite positioning
            offset_y: Y offset for sprite positioning
            frame: Initial animation frame
        """
        super().__init__(entity)
        self.logger = logging.getLogger("SpriteComponent")
        
        # Basic sprite properties
        self.image: Optional[pygame.Surface] = None
        self.image_key: str = image_key
        self.visible: bool = visible
        self.offset_x: float = offset_x
        self.offset_y: float = offset_y
        
        # Animation properties
        self.animation: Optional[Dict[str, List[pygame.Surface]]] = None
        self.current_animation: str = "idle"
        self.frame_index: int = frame
        self.frame_time: float = 0.0
        self.frame_duration: float = 0.1
        self.animation_complete: bool = False
        
        # Transform properties
        self.flip_x: bool = False
        self.flip_y: bool = False
        self.layer: int = 0
        self.scale: float = 1.0
        self.rotation: float = 0.0
        self.alpha: int = 255
        
        # Load initial image if provided
        if image_key:
            self.load_image(image_key)
    
    def load_image(self, image_key: str) -> bool:
        """Load an image from the asset manager.
        
        Args:
            image_key: Key for the image in the asset manager
            
        Returns:
            bool: True if image loaded successfully, False otherwise
        """
        try:
            from asset_manager import AssetManager
            asset_manager = AssetManager.get_instance()
            if not asset_manager:
                self.logger.error("AssetManager not available")
                return False
                
            self.image = asset_manager.get_image(image_key)
            if not self.image:
                self.logger.error(f"Failed to load image: {image_key}")
                return False
                
            self.image_key = image_key
            self.logger.debug(f"Successfully loaded image: {image_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading image {image_key}: {str(e)}")
            return False
    
    def play_animation(self, animation_name: str, reset: bool = True) -> bool:
        """Play a specific animation.
        
        Args:
            animation_name: Name of the animation to play
            reset: Whether to reset the animation to the first frame
            
        Returns:
            bool: True if animation exists and was started, False otherwise
        """
        if not self.animation or animation_name not in self.animation:
            self.logger.warning(f"Animation not found: {animation_name}")
            return False
            
        self.current_animation = animation_name
        if reset:
            self.frame_index = 0
            self.frame_time = 0.0
            self.animation_complete = False
            
        self.logger.debug(f"Playing animation: {animation_name}")
        return True
    
    def update(self, dt: float) -> None:
        """Update animation frame.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.animation or self.current_animation not in self.animation:
            return
            
        self.frame_time += dt
        if self.frame_time >= self.frame_duration:
            self.frame_time = 0
            self.frame_index = (self.frame_index + 1) % len(self.animation[self.current_animation])
            
            # Check if animation completed one cycle
            if self.frame_index == 0:
                self.animation_complete = True
                self.logger.debug(f"Animation cycle completed: {self.current_animation}")
    
    def get_current_frame(self) -> Optional[pygame.Surface]:
        """Get the current animation frame or static image.
        
        Returns:
            Optional[pygame.Surface]: The current frame or None if no image available
        """
        try:
            if self.animation and self.current_animation in self.animation:
                frame = self.animation[self.current_animation][self.frame_index]
            else:
                frame = self.image
                
            if not frame:
                self.logger.warning("No frame or image available")
                return None
                
            # Apply transformations
            if self.flip_x or self.flip_y:
                frame = pygame.transform.flip(frame, self.flip_x, self.flip_y)
            if self.scale != 1.0:
                frame = pygame.transform.scale(frame, 
                    (int(frame.get_width() * self.scale), 
                     int(frame.get_height() * self.scale)))
            if self.rotation != 0.0:
                frame = pygame.transform.rotate(frame, self.rotation)
            if self.alpha != 255:
                frame.set_alpha(self.alpha)
                
            return frame
            
        except Exception as e:
            self.logger.error(f"Error getting current frame: {str(e)}")
            return None
    
    def add_animation(self, name: str, frames: List[pygame.Surface], duration: float = 0.1) -> bool:
        """Add a new animation sequence.
        
        Args:
            name: Name of the animation
            frames: List of frames for the animation
            duration: Duration of each frame in seconds
            
        Returns:
            bool: True if animation was added successfully
        """
        try:
            if not frames:
                self.logger.error(f"Cannot add empty animation: {name}")
                return False
                
            if not self.animation:
                self.animation = {}
                
            self.animation[name] = frames
            self.frame_duration = duration
            self.logger.debug(f"Added animation: {name} with {len(frames)} frames")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding animation {name}: {str(e)}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "image_key": self.image_key,
            "current_animation": self.current_animation,
            "frame_index": self.frame_index,
            "frame_time": self.frame_time,
            "frame_duration": self.frame_duration,
            "flip_x": self.flip_x,
            "flip_y": self.flip_y,
            "visible": self.visible,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "layer": self.layer,
            "scale": self.scale,
            "rotation": self.rotation,
            "alpha": self.alpha
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], entity: 'Entity') -> 'SpriteComponent':
        """Create component from dictionary."""
        component = cls(
            entity=entity,
            image_key=data.get("image_key"),
            visible=data.get("visible", True),
            offset_x=data.get("offset_x", 0.0),
            offset_y=data.get("offset_y", 0.0),
            frame=data.get("frame_index", 0)
        )
        
        # Set additional properties
        component.flip_x = data.get("flip_x", False)
        component.flip_y = data.get("flip_y", False)
        component.layer = data.get("layer", 0)
        component.scale = data.get("scale", 1.0)
        component.rotation = data.get("rotation", 0.0)
        component.alpha = data.get("alpha", 255)
        
        return component 