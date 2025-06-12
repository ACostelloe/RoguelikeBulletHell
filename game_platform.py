import pygame
import random
import math
from visual_effects import visual_effects, biome_visuals, apply_tint, apply_overlay

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type='normal', biome_type='grass', overlays=None):
        super().__init__()
        self.platform_type = platform_type
        self.biome_type = biome_type
        self.width = width
        self.height = height
        self.overlays = overlays or {}
        
        # Create base surface
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Platform properties
        self.health = 100
        self.hit_flash = 0
        self.particles = []
        self.interaction_cooldown = 0
        self.effect_cooldown = 0
        
        # Biome-specific tint configurations
        self.biome_tints = {
            "forest": ((34, 139, 34), 0.3),  # Forest green tint
            "lava": ((255, 69, 0), 0.4),     # Orange-red tint
            "tech": ((70, 130, 180), 0.4),   # Steel blue tint
            "ice": ((173, 216, 230), 0.4),   # Light blue tint
            "grass": ((144, 238, 144), 0.2)  # Light green tint
        }
        
        # Biome-specific overlay configurations
        self.biome_overlay_types = {
            "forest": None,
            "lava": "cracks",
            "tech": "glow",
            "ice": "frost",
            "grass": None
        }
        
        # Platform effects
        self.bounce_power = 20
        self.speed_multiplier = 1.5
        self.jump_multiplier = 1.5
        self.heal_amount = 20
        self.heal_cooldown = 300
        self.shield_duration = 180
        self.slow_factor = 0.5
        self.damage_multiplier = 2.0
        self.grapple_multiplier = 1.5
        self.repel_force = 10
        self.cooldown_time = 60
        self.break_chance = 0.3
        
        # Moving platform properties
        self.original_pos = (x, y)
        self.move_speed = 2
        self.move_range = 100
        
        # Collapsing platform properties
        self.collapse_time = 60
        self.collapse_timer = 0
        self.is_collapsing = False
        
        # Bouncy platform properties
        self.bounce_cooldown = 30
        self.bounce_timer = 0
        
        # Grapple boost platform properties
        self.boost_duration = 180
        self.boost_timer = 0
        
        # Spike platform properties
        self.spike_damage = 10
        self.spike_cooldown = 30
        self.spike_timer = 0
        
        # Visual properties
        self.is_win_platform = False
        self.border_width = 2
        self.border_color = (100, 100, 100)
        
        # Initialize platform appearance
        self.update_appearance()

    def _draw_platform(self):
        """Draw the platform with appropriate tiles and effects."""
        # Clear the surface
        self.image.fill((0, 0, 0, 0))
        
        # Get base tiles based on platform type and biome
        biome_suffix = f'_{self.biome_type}' if self.biome_type in ['grass', 'lava', 'tech', 'ice', 'forest'] else ''
        type_suffix = '_damaged' if self.platform_type == 'damaging' else ''
        
        # Draw the base platform
        if self.width <= 32:
            # Single tile platform
            tile_name = f'single{type_suffix or biome_suffix}'
            tile = None  # TODO: Replace with new tile system
            if not tile and biome_suffix:
                tile = None  # TODO: Replace with new tile system
            if not tile:
                tile = None  # TODO: Replace with new tile system
            if tile:
                self.image.blit(tile, (0, 0))
        else:
            # Multi-tile platform
            # Left edge
            left_tile = self._get_platform_tile('left', type_suffix, biome_suffix)
            if left_tile:
                self.image.blit(left_tile, (0, 0))
            
            # Middle tiles
            middle_tile = self._get_platform_tile('middle', type_suffix, biome_suffix)
            if middle_tile:
                for x in range(32, self.width - 32, 32):
                    self.image.blit(middle_tile, (x, 0))
            
            # Right edge
            right_tile = self._get_platform_tile('right', type_suffix, biome_suffix)
            if right_tile:
                self.image.blit(right_tile, (self.width - 32, 0))
        
        # Apply biome-specific effects
        if self.biome_type in self.biome_tints:
            tint_color, tint_strength = self.biome_tints[self.biome_type]
            self.image = apply_tint(self.image, tint_color, tint_strength)
        
        # Apply biome-specific overlay
        overlay_type = self.biome_overlay_types.get(self.biome_type)
        if overlay_type and overlay_type in self.overlays:
            self.image = apply_overlay(self.image, self.overlays[overlay_type], alpha=150)

    def _get_platform_tile(self, position, type_suffix, biome_suffix):
        """Helper method to get platform tiles with fallback options."""
        tile_name = f'{position}{type_suffix or biome_suffix}'
        tile = None  # TODO: Replace with new tile system
        if not tile and biome_suffix:
            tile = None  # TODO: Replace with new tile system
        if not tile:
            tile = None  # TODO: Replace with new tile system
        return tile

    def update_appearance(self):
        """Update the platform's visual appearance based on its type."""
        self._draw_platform()
        
        # Add hit flash effect
        if self.hit_flash > 0:
            self.image.set_alpha(128)
        else:
            self.image.set_alpha(255)

    def add_particles(self, count):
        """Add particles for visual effects."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            self.particles.append({
                'pos': (self.rect.centerx, self.rect.centery),
                'vel': (math.cos(angle) * speed, math.sin(angle) * speed),
                'life': 30,
                'color': self.image.get_at((self.rect.width//2, self.rect.height-5))
            })

    def update(self, player=None):
        """Update platform state and handle interactions."""
        # Update moving platform
        if self.platform_type == 'moving':
            self.rect.y = self.original_pos[1] + math.sin(pygame.time.get_ticks() * 0.001 * self.move_speed) * self.move_range
        
        # Update collapsing platform
        if self.platform_type == 'collapsing' and self.is_collapsing:
            self.collapse_timer += 1
            if self.collapse_timer >= self.collapse_time:
                self.kill()
        
        # Update bouncy platform
        if self.platform_type == 'bouncy':
            if self.bounce_timer > 0:
                self.bounce_timer -= 1
        
        # Update grapple boost platform
        if self.platform_type == 'grapple_boost':
            if self.boost_timer > 0:
                self.boost_timer -= 1
        
        # Update spike platform
        if self.platform_type == 'spike':
            if self.spike_timer > 0:
                self.spike_timer -= 1
        
        # Update particles
        for particle in self.particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
            else:
                particle['pos'] = (particle['pos'][0] + particle['vel'][0],
                                 particle['pos'][1] + particle['vel'][1])
                particle['vel'] = (particle['vel'][0] * 0.95,
                                 particle['vel'][1] * 0.95 + 0.2)
        
        # Update cooldowns
        if self.interaction_cooldown > 0:
            self.interaction_cooldown -= 1
        if self.effect_cooldown > 0:
            self.effect_cooldown -= 1

    def handle_collision(self, player):
        """Handle collision with player."""
        if self.platform_type == 'damaging':
            player.take_damage(10)
        elif self.platform_type == 'bouncy' and self.bounce_timer <= 0:
            player.velocity_y = -self.bounce_power
            self.bounce_timer = self.bounce_cooldown
        elif self.platform_type == 'grapple_boost' and self.boost_timer <= 0:
            player.grapple_multiplier = self.grapple_multiplier
            self.boost_timer = self.boost_duration
        elif self.platform_type == 'spike' and self.spike_timer <= 0:
            player.take_damage(self.spike_damage)
            self.spike_timer = self.spike_cooldown
        elif self.platform_type == 'collapsing' and not self.is_collapsing:
            self.is_collapsing = True
            self.collapse_timer = 0

    def handle_grapple(self, player):
        """Handle grappling hook interaction."""
        if self.platform_type == 'grapple_boost':
            player.grapple_multiplier = self.grapple_multiplier
            self.boost_timer = self.boost_duration
        elif self.platform_type == 'damaging':
            player.take_damage(5)

    def draw(self, screen, camera_x, camera_y):
        """Draw the platform and its effects."""
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))
        for particle in self.particles:
            pygame.draw.circle(screen, particle['color'], 
                             (int(particle['pos'][0] - camera_x), int(particle['pos'][1] - camera_y)), 2) 