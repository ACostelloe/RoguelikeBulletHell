import pygame
import random
import math
from visual_effects import tileset_manager, visual_effects, biome_visuals

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type='normal', biome_type='sand'):
        super().__init__()
        self.platform_type = platform_type
        self.biome_type = biome_type
        self.width = width
        self.height = height
        
        # Create base surface
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Load tileset if not already loaded
        if 'platforms' not in tileset_manager.tilesets:
            tileset_manager.load_tileset('platforms', 'assets/platform_tiles', 32, 32)
            tileset_manager.create_tile_mapping('platforms', {
                'left': 'left',
                'middle': 'middle',
                'right': 'right',
                'single': 'single',
                'left_damaged': 'left_damaged',
                'middle_damaged': 'middle_damaged',
                'right_damaged': 'right_damaged',
                'left_ice': 'left_ice',
                'middle_ice': 'middle_ice',
                'right_ice': 'right_ice',
                'left_grass': 'left_grass',
                'middle_grass': 'middle_grass',
                'right_grass': 'right_grass'
            })
        
        # Platform properties
        self.health = 100
        self.hit_flash = 0
        self.particles = []
        self.interaction_cooldown = 0
        self.effect_cooldown = 0
        
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
        
        # Get biome colors
        colors = biome_visuals.get_biome_colors(self.biome_type)
        
        # Draw base platform
        if self.width <= 32:
            # Single tile platform
            tile_name = 'single'
            if self.platform_type == 'damaging':
                tile_name = 'middle_damaged'
            elif self.biome_type == 'ice':
                tile_name = 'middle_ice'
            elif self.biome_type == 'grass':
                tile_name = 'middle_grass'
            
            tile = tileset_manager.get_tile('platforms', tile_name)
            if tile:
                self.image.blit(tile, (0, 0))
        else:
            # Multi-tile platform
            # Left edge
            left_tile_name = 'left'
            if self.platform_type == 'damaging':
                left_tile_name = 'left_damaged'
            elif self.biome_type == 'ice':
                left_tile_name = 'left_ice'
            elif self.biome_type == 'grass':
                left_tile_name = 'left_grass'
            
            left_tile = tileset_manager.get_tile('platforms', left_tile_name)
            if left_tile:
                self.image.blit(left_tile, (0, 0))
            
            # Middle tiles
            middle_tile_name = 'middle'
            if self.platform_type == 'damaging':
                middle_tile_name = 'middle_damaged'
            elif self.biome_type == 'ice':
                middle_tile_name = 'middle_ice'
            elif self.biome_type == 'grass':
                middle_tile_name = 'middle_grass'
            
            middle_tile = tileset_manager.get_tile('platforms', middle_tile_name)
            if middle_tile:
                for x in range(32, self.width - 32, 32):
                    self.image.blit(middle_tile, (x, 0))
            
            # Right edge
            right_tile_name = 'right'
            if self.platform_type == 'damaging':
                right_tile_name = 'right_damaged'
            elif self.biome_type == 'ice':
                right_tile_name = 'right_ice'
            elif self.biome_type == 'grass':
                right_tile_name = 'right_grass'
            
            right_tile = tileset_manager.get_tile('platforms', right_tile_name)
            if right_tile:
                self.image.blit(right_tile, (self.width - 32, 0))
        
        # Apply biome colors
        self.image = biome_visuals.apply_biome_colors(self.image, self.biome_type)
        
        # Apply platform type effects
        if self.platform_type == 'moving':
            # Add movement indicator
            glow = visual_effects.apply_glow(self.image, colors['highlight'], 50)
            self.image.blit(glow, (0, 0))
        elif self.platform_type == 'collapsing':
            # Add cracking effect
            self.image = visual_effects.apply_distortion(self.image, 0.05)
        elif self.platform_type == 'grapple_boost':
            # Add magical effect
            glow = visual_effects.apply_glow(self.image, (255, 215, 0), 75)
            self.image.blit(glow, (0, 0))
            self.image = visual_effects.apply_noise(self.image, 0.1)
            
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
        if self.interaction_cooldown > 0:
            return
        
        if self.platform_type == 'breakable' and player.vel_y > 0:
            self.health -= 20
            self.hit_flash = 10
            self.add_particles(5)
            if self.health <= 0:
                self.kill()
        
        elif self.platform_type == 'bouncy' and player.vel_y > 0:
            player.vel_y = -self.bounce_power
            self.add_particles(3)
            self.interaction_cooldown = 30
        
        elif self.platform_type == 'slippery':
            player.vel_x *= 1.1
        
        elif self.platform_type == 'damaging' and player.vel_y > 0:
            player.take_damage(1)
            self.add_particles(2)
            self.interaction_cooldown = 60
            
        elif self.platform_type == 'speed_boost' and self.effect_cooldown <= 0:
            player.move_speed *= self.speed_multiplier
            self.effect_cooldown = self.effect_duration
            self.add_particles(3)
            
        elif self.platform_type == 'jump_boost' and self.effect_cooldown <= 0:
            player.jump_power *= self.jump_multiplier
            self.effect_cooldown = self.effect_duration
            self.add_particles(3)
            
        elif self.platform_type == 'healing' and self.effect_cooldown <= 0:
            player.health = min(player.health + self.heal_amount, player.stats.max_health)
            self.effect_cooldown = self.heal_cooldown
            self.add_particles(3)
            
        elif self.platform_type == 'shield' and self.effect_cooldown <= 0:
            player.invincible = True
            player.invincibility_timer = self.shield_duration
            self.effect_cooldown = self.effect_duration
            self.add_particles(3)
            
        elif self.platform_type == 'time_slow' and self.effect_cooldown <= 0:
            # Slow down all enemies
            for enemy in player.game.enemies:
                enemy.speed *= self.slow_factor
            self.effect_cooldown = self.effect_duration
            self.add_particles(3)
            
        elif self.platform_type == 'double_damage' and self.effect_cooldown <= 0:
            player.bullet_damage *= self.damage_multiplier
            self.effect_cooldown = self.effect_duration
            self.add_particles(3)

    def handle_grapple(self, player):
        """Handle grapple interaction with platform."""
        if self.platform_type == 'grapple_boost':
            player.hook_range *= self.grapple_multiplier
            self.effect_cooldown = self.effect_duration
            self.add_particles(3)
            
        elif self.platform_type == 'grapple_repel':
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                player.vel_x += (dx / length) * self.repel_force
                player.vel_y += (dy / length) * self.repel_force
            self.add_particles(3)
            
        elif self.platform_type == 'grapple_cooldown':
            player.hook_cooldown = self.cooldown_time
            self.add_particles(2)
            
        elif self.platform_type == 'grapple_break':
            if random.random() < self.break_chance:
                player.hook_active = False
                player.hook_cooldown = self.cooldown_time
                self.add_particles(5)

    def draw(self, screen, camera_x, camera_y):
        """Draw the platform and its particles."""
        # Draw platform
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        screen.blit(self.image, (screen_x, screen_y))
        
        # Draw particles
        for particle in self.particles:
            alpha = int((particle['life'] / 30) * 255)
            color = (*particle['color'][:3], alpha)
            pos_x = particle['pos'][0] - camera_x
            pos_y = particle['pos'][1] - camera_y
            pygame.draw.circle(screen, color, (int(pos_x), int(pos_y)), 2) 