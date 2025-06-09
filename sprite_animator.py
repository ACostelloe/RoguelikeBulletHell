import pygame
import os
from typing import Dict, List, Optional

class SpriteAnimator:
    def __init__(self):
        self.animations = {}
        self.current_animation = None
        self.current_frame = 0
        self.time_accumulator = 0.0
        self.frame_duration = 0.15  # seconds per frame
        self.loop = True
        
    def load_animations(self, base_path, animation_map=None):
        """
        Loads animations from a directory. If only a single image is found, uses it as a static sprite.
        animation_map: dict mapping animation state to filename (without extension)
        """
        if animation_map is None:
            animation_map = {'idle': 'Idle'}
        for state, name in animation_map.items():
            frames = []
            # Try to load as a spritesheet (multi-frame)
            spritesheet_path = os.path.join(base_path, f"{name}.png")
            if os.path.exists(spritesheet_path):
                image = pygame.image.load(spritesheet_path).convert_alpha()
                width, height = image.get_size()
                # If the image is wider than tall, assume horizontal strip
                if width > height:
                    frame_count = width // height
                    for i in range(frame_count):
                        frame = image.subsurface((i * height, 0, height, height))
                        frames.append(frame)
                else:
                    # Single frame
                    frames.append(image)
            else:
                # Try to load as a single image
                single_path = os.path.join(base_path, f"{name}.png")
                if os.path.exists(single_path):
                    image = pygame.image.load(single_path).convert_alpha()
                    frames.append(image)
            if not frames:
                # Fallback: create a placeholder
                surf = pygame.Surface((32, 32), pygame.SRCALPHA)
                surf.fill((255, 0, 255))
                frames.append(surf)
            self.animations[state] = frames
        # Set default animation
        if self.current_animation is None and self.animations:
            self.set_animation(next(iter(self.animations)))
        
    def set_animation(self, animation, loop=True):
        """Set the current animation and reset frame counter."""
        if animation != self.current_animation:
            self.current_animation = animation
            self.current_frame = 0
            self.time_accumulator = 0.0
            self.loop = loop
            
    def update(self, dt):
        """Update animation frame based on time."""
        if self.current_animation is None:
            return
        frames = self.animations.get(self.current_animation, [])
        if len(frames) <= 1:
            return  # Static sprite, no animation
        self.time_accumulator += dt
        if self.time_accumulator > self.frame_duration:
            self.time_accumulator -= self.frame_duration
            self.current_frame += 1
            if self.current_frame >= len(frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(frames) - 1
            
    def get_current_frame(self):
        """Get the current animation frame."""
        if self.current_animation is None:
            return None
        frames = self.animations.get(self.current_animation, [])
        if not frames:
            return None
        return frames[self.current_frame]
        
    def is_animation_finished(self):
        """Check if the current animation has finished."""
        if self.current_animation is None:
            return True
        frames = self.animations.get(self.current_animation, [])
        return self.current_frame == len(frames) - 1 and not self.loop 