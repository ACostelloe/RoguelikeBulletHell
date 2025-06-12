"""
Particle system for visual effects.
"""
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
import pygame
import random
import math
from entities import Entity, Component
from logger import logger
import traceback

@dataclass
class ParticleComponent(Component):
    """Component for handling particles."""
    emitter_id: str = ""
    active: bool = True
    rate: float = 10.0
    burst: int = 0
    lifetime: float = 1.0
    speed: float = 100.0
    size: float = 4.0
    color: Tuple[int, int, int] = (255, 255, 255)
    alpha: int = 255
    gravity: float = 0.0
    rotation: float = 0.0
    rotation_speed: float = 0.0
    scale: float = 1.0
    scale_speed: float = 0.0
    particles: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "emitter_id": self.emitter_id,
            "active": self.active,
            "rate": self.rate,
            "burst": self.burst,
            "lifetime": self.lifetime,
            "speed": self.speed,
            "size": self.size,
            "color": self.color,
            "alpha": self.alpha,
            "gravity": self.gravity,
            "rotation": self.rotation,
            "rotation_speed": self.rotation_speed,
            "scale": self.scale,
            "scale_speed": self.scale_speed,
            "particles": self.particles
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParticleComponent':
        """Create component from dictionary."""
        return cls(
            emitter_id=data["emitter_id"],
            active=data["active"],
            rate=data["rate"],
            burst=data["burst"],
            lifetime=data["lifetime"],
            speed=data["speed"],
            size=data["size"],
            color=tuple(data["color"]),
            alpha=data["alpha"],
            gravity=data["gravity"],
            rotation=data["rotation"],
            rotation_speed=data["rotation_speed"],
            scale=data["scale"],
            scale_speed=data["scale_speed"],
            particles=data["particles"]
        )

class ParticleSystem:
    """Manages particle effects."""
    
    def __init__(self):
        """Initialize the particle system."""
        self.particles = []
        self.emitters = []
        self.entities = []  # Initialize entities list
        self.emitters: Dict[str, Dict[str, Any]] = {}
        
    def create_emitter(self, emitter_id: str, properties: Dict[str, Any]) -> None:
        """Create a new particle emitter."""
        try:
            self.emitters[emitter_id] = {
                "rate": properties.get("rate", 10.0),
                "burst": properties.get("burst", 0),
                "lifetime": properties.get("lifetime", 1.0),
                "speed": properties.get("speed", 100.0),
                "size": properties.get("size", 4.0),
                "color": properties.get("color", (255, 255, 255)),
                "alpha": properties.get("alpha", 255),
                "gravity": properties.get("gravity", 0.0),
                "rotation": properties.get("rotation", 0.0),
                "rotation_speed": properties.get("rotation_speed", 0.0),
                "scale": properties.get("scale", 1.0),
                "scale_speed": properties.get("scale_speed", 0.0),
                "shape": properties.get("shape", "circle"),
                "spread": properties.get("spread", 360.0),
                "texture": properties.get("texture", None)
            }
            
        except Exception as e:
            logger.error(f"Error creating emitter: {str(e)}")
            logger.error(traceback.format_exc())
            
    def emit_particles(self, entity: Entity, emitter_id: str, count: Optional[int] = None) -> None:
        """Emit particles from an entity."""
        try:
            # Get or create particle component
            particle = entity.get_component(ParticleComponent)
            if not particle:
                particle = ParticleComponent(entity)
                entity.add_component(particle)
                
            # Get emitter properties
            emitter = self.emitters.get(emitter_id)
            if not emitter:
                return
                
            # Set component properties
            particle.emitter_id = emitter_id
            particle.rate = emitter["rate"]
            particle.burst = emitter["burst"]
            particle.lifetime = emitter["lifetime"]
            particle.speed = emitter["speed"]
            particle.size = emitter["size"]
            particle.color = emitter["color"]
            particle.alpha = emitter["alpha"]
            particle.gravity = emitter["gravity"]
            particle.rotation = emitter["rotation"]
            particle.rotation_speed = emitter["rotation_speed"]
            particle.scale = emitter["scale"]
            particle.scale_speed = emitter["scale_speed"]
            
            # Get entity transform
            transform = entity.get_component(TransformComponent)
            if not transform:
                return
                
            # Emit particles
            if count is None:
                count = emitter["burst"] if emitter["burst"] > 0 else 1
                
            for _ in range(count):
                # Calculate random angle
                angle = random.uniform(0, emitter["spread"])
                rad = math.radians(angle)
                
                # Calculate velocity
                speed = random.uniform(0.8, 1.2) * emitter["speed"]
                vx = math.cos(rad) * speed
                vy = math.sin(rad) * speed
                
                # Create particle
                particle_data = {
                    "x": transform.x,
                    "y": transform.y,
                    "vx": vx,
                    "vy": vy,
                    "size": random.uniform(0.8, 1.2) * emitter["size"],
                    "color": emitter["color"],
                    "alpha": emitter["alpha"],
                    "rotation": random.uniform(0, 360),
                    "scale": emitter["scale"],
                    "lifetime": random.uniform(0.8, 1.2) * emitter["lifetime"],
                    "elapsed": 0.0,
                    "shape": emitter["shape"],
                    "texture": emitter["texture"]
                }
                
                particle.particles.append(particle_data)
                
        except Exception as e:
            logger.error(f"Error emitting particles: {str(e)}")
            logger.error(traceback.format_exc())
            
    def update(self, dt: float) -> None:
        """Update all particles."""
        try:
            for entity in self.entities:
                particle = entity.get_component(ParticleComponent)
                if not particle or not particle.active:
                    continue
                    
                # Update existing particles
                for p in particle.particles[:]:
                    p["elapsed"] += dt
                    
                    # Remove dead particles
                    if p["elapsed"] >= p["lifetime"]:
                        particle.particles.remove(p)
                        continue
                        
                    # Calculate life ratio
                    life_ratio = p["elapsed"] / p["lifetime"]
                    
                    # Update position
                    p["x"] += p["vx"] * dt
                    p["y"] += p["vy"] * dt
                    
                    # Apply gravity
                    p["vy"] += particle.gravity * dt
                    
                    # Update rotation
                    p["rotation"] += particle.rotation_speed * dt
                    
                    # Update scale
                    p["scale"] += particle.scale_speed * dt
                    
                    # Update alpha
                    p["alpha"] = int(particle.alpha * (1.0 - life_ratio))
                    
                # Emit new particles
                if particle.rate > 0:
                    particle.emit_time += dt
                    while particle.emit_time >= 1.0 / particle.rate:
                        self.emit_particles(entity, particle.emitter_id, 1)
                        particle.emit_time -= 1.0 / particle.rate
                        
        except Exception as e:
            logger.error(f"Error updating particles: {str(e)}")
            logger.error(traceback.format_exc())
            
    def render(self, surface: pygame.Surface, camera: Tuple[float, float]) -> None:
        """Render all particles."""
        try:
            for entity in self.entities:
                particle = entity.get_component(ParticleComponent)
                if not particle or not particle.active:
                    continue
                    
                for p in particle.particles:
                    # Calculate screen position
                    screen_x = p["x"] - camera[0]
                    screen_y = p["y"] - camera[1]
                    
                    # Skip if off screen
                    if (screen_x < -p["size"] or screen_x > surface.get_width() + p["size"] or
                        screen_y < -p["size"] or screen_y > surface.get_height() + p["size"]):
                        continue
                        
                    # Draw particle
                    if p["texture"]:
                        # Draw textured particle
                        texture = p["texture"]
                        size = int(p["size"] * p["scale"])
                        scaled = pygame.transform.scale(texture, (size, size))
                        rotated = pygame.transform.rotate(scaled, p["rotation"])
                        rect = rotated.get_rect(center=(screen_x, screen_y))
                        rotated.set_alpha(p["alpha"])
                        surface.blit(rotated, rect)
                    else:
                        # Draw shape particle
                        size = int(p["size"] * p["scale"])
                        if p["shape"] == "circle":
                            pygame.draw.circle(surface, p["color"], (int(screen_x), int(screen_y)), size)
                        elif p["shape"] == "square":
                            rect = pygame.Rect(screen_x - size, screen_y - size, size * 2, size * 2)
                            pygame.draw.rect(surface, p["color"], rect)
                        elif p["shape"] == "triangle":
                            points = [
                                (screen_x, screen_y - size),
                                (screen_x - size, screen_y + size),
                                (screen_x + size, screen_y + size)
                            ]
                            pygame.draw.polygon(surface, p["color"], points)
                            
        except Exception as e:
            logger.error(f"Error rendering particles: {str(e)}")
            logger.error(traceback.format_exc())
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert system to dictionary."""
        return {
            "emitters": self.emitters
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParticleSystem':
        """Create system from dictionary."""
        system = cls()
        system.emitters = data["emitters"]
        return system 

# --- ParticleManager compatibility wrapper ---
class ParticleManager(ParticleSystem):
    """Alias for ParticleSystem to maintain compatibility with code expecting ParticleManager."""
    pass 