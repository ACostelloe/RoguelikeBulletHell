import pygame
from typing import Dict, Tuple
from world_manager import WorldManager
from config import ZONE_SIZE, BIOME_SETTINGS

class ZoneDebugOverlay:
    def __init__(self, world_manager: WorldManager):
        self.world_manager = world_manager
        self.font = pygame.font.Font(None, 24)
        self.show_grid = True
        self.show_biome = True
        self.show_spawns = True
        self.show_events = True
        
        # Colors
        self.grid_color = (100, 100, 100, 128)  # Semi-transparent gray
        self.biome_colors = {
            "forest": (34, 139, 34, 64),    # Semi-transparent forest green
            "tech": (70, 130, 180, 64),     # Semi-transparent steel blue
            "lava": (139, 0, 0, 64),        # Semi-transparent dark red
            "ice": (135, 206, 235, 64)      # Semi-transparent sky blue
        }
        self.spawn_color = (255, 255, 0, 128)  # Semi-transparent yellow
        self.event_color = (255, 0, 255, 128)  # Semi-transparent magenta

    def toggle_grid(self):
        """Toggle the grid display."""
        self.show_grid = not self.show_grid

    def toggle_biome(self):
        """Toggle the biome display."""
        self.show_biome = not self.show_biome

    def toggle_spawns(self):
        """Toggle the spawn point display."""
        self.show_spawns = not self.show_spawns

    def toggle_events(self):
        """Toggle the event display."""
        self.show_events = not self.show_events

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        """Draw the debug overlay."""
        # Convert camera position to zone coordinates
        zone_x = int(camera_x / ZONE_SIZE)
        zone_y = int(camera_y / ZONE_SIZE)
        
        # Draw visible zones
        for x in range(zone_x - 2, zone_x + 3):
            for y in range(zone_y - 2, zone_y + 3):
                self._draw_zone_debug(screen, x, y, camera_x, camera_y)

    def _draw_zone_debug(self, screen: pygame.Surface, zone_x: int, zone_y: int, 
                        camera_x: float, camera_y: float):
        """Draw debug information for a single zone."""
        zone = self.world_manager.get_zone_at(zone_x * ZONE_SIZE, zone_y * ZONE_SIZE)
        if not zone:
            return

        # Calculate screen position
        screen_x = zone_x * ZONE_SIZE - camera_x
        screen_y = zone_y * ZONE_SIZE - camera_y

        # Draw grid
        if self.show_grid:
            pygame.draw.rect(screen, self.grid_color, 
                           (screen_x, screen_y, ZONE_SIZE, ZONE_SIZE), 1)

        # Draw biome
        if self.show_biome and zone.biome in self.biome_colors:
            biome_surface = pygame.Surface((ZONE_SIZE, ZONE_SIZE), pygame.SRCALPHA)
            biome_surface.fill(self.biome_colors[zone.biome])
            screen.blit(biome_surface, (screen_x, screen_y))
            
            # Draw biome name
            biome_text = self.font.render(zone.biome, True, (255, 255, 255))
            screen.blit(biome_text, (screen_x + 5, screen_y + 5))

        # Draw zone template name
        template_text = self.font.render(zone.name, True, (255, 255, 255))
        screen.blit(template_text, (screen_x + 5, screen_y + 25))

        # Draw spawns
        if self.show_spawns:
            # Draw enemy spawns
            for enemy in zone.enemies:
                spawn_x = screen_x + enemy.x * ZONE_SIZE
                spawn_y = screen_y + enemy.y * ZONE_SIZE
                pygame.draw.circle(screen, self.spawn_color, 
                                 (int(spawn_x), int(spawn_y)), 5)
                
                # Draw enemy type
                enemy_text = self.font.render(enemy.type, True, (255, 255, 255))
                screen.blit(enemy_text, (spawn_x + 10, spawn_y - 10))

            # Draw loot spawns
            for loot in zone.loot:
                spawn_x = screen_x + loot.x * ZONE_SIZE
                spawn_y = screen_y + loot.y * ZONE_SIZE
                pygame.draw.circle(screen, self.spawn_color, 
                                 (int(spawn_x), int(spawn_y)), 3)
                
                # Draw loot type and rarity
                loot_text = self.font.render(f"{loot.type} ({loot.rarity})", 
                                           True, (255, 255, 255))
                screen.blit(loot_text, (spawn_x + 10, spawn_y - 10))

        # Draw events
        if self.show_events and zone.events:
            event_text = self.font.render("Events:", True, (255, 255, 255))
            screen.blit(event_text, (screen_x + 5, screen_y + 45))
            
            for i, event in enumerate(zone.events):
                event_text = self.font.render(event, True, (255, 255, 255))
                screen.blit(event_text, (screen_x + 5, screen_y + 65 + i * 20))

    def draw_controls(self, screen: pygame.Surface):
        """Draw the debug control information."""
        controls = [
            "Debug Controls:",
            "G - Toggle Grid",
            "B - Toggle Biome",
            "S - Toggle Spawns",
            "E - Toggle Events"
        ]
        
        y = 10
        for control in controls:
            text = self.font.render(control, True, (255, 255, 255))
            screen.blit(text, (10, y))
            y += 25 