import pygame
import math
import random

class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.enemy_patterns = self.get_patterns()
        self.background_color = (20, 20, 30)  # Dark blue-gray
        self.grid_size = 40
        self.grid_color = (40, 40, 50)
        self.grid_alpha = 50

    def get_patterns(self):
        patterns = {
            1: [
                {"type": "basic", "count": 5, "spawn_delay": 60, "formation": "circle"},
                {"type": "fast", "count": 3, "spawn_delay": 45, "formation": "line"},
                {"type": "tank", "count": 2, "spawn_delay": 90, "formation": "v"}
            ],
            2: [
                {"type": "basic", "count": 8, "spawn_delay": 50, "formation": "circle"},
                {"type": "fast", "count": 5, "spawn_delay": 40, "formation": "line"},
                {"type": "tank", "count": 3, "spawn_delay": 80, "formation": "v"},
                {"type": "shooter", "count": 2, "spawn_delay": 70, "formation": "cross"}
            ],
            3: [
                {"type": "basic", "count": 10, "spawn_delay": 45, "formation": "circle"},
                {"type": "fast", "count": 7, "spawn_delay": 35, "formation": "line"},
                {"type": "tank", "count": 4, "spawn_delay": 70, "formation": "v"},
                {"type": "shooter", "count": 3, "spawn_delay": 60, "formation": "cross"},
                {"type": "boss", "count": 1, "spawn_delay": 120, "formation": "center"}
            ]
        }
        return patterns.get(self.level_number, patterns[1])

    def get_spawn_positions(self, formation, count, screen_width, screen_height):
        positions = []
        center_x = screen_width // 2
        center_y = screen_height // 2
        radius = min(screen_width, screen_height) // 4

        if formation == "circle":
            for i in range(count):
                angle = (2 * math.pi * i) / count
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions.append((x, y))

        elif formation == "line":
            spacing = screen_width // (count + 1)
            for i in range(count):
                x = spacing * (i + 1)
                y = 50
                positions.append((x, y))

        elif formation == "v":
            spacing = screen_width // (count + 1)
            for i in range(count):
                x = spacing * (i + 1)
                y = 50 + (i * 30)
                positions.append((x, y))

        elif formation == "cross":
            if count >= 4:
                positions = [
                    (center_x, 50),  # Top
                    (center_x, screen_height - 50),  # Bottom
                    (50, center_y),  # Left
                    (screen_width - 50, center_y)  # Right
                ]
                # Add extra positions if count > 4
                for i in range(count - 4):
                    angle = (2 * math.pi * i) / (count - 4)
                    x = center_x + radius * math.cos(angle)
                    y = center_y + radius * math.sin(angle)
                    positions.append((x, y))

        elif formation == "center":
            positions = [(center_x, center_y)]

        return positions

    def draw_background(self, screen):
        # Draw background
        screen.fill(self.background_color)
        
        # Draw grid
        grid_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for x in range(0, screen.get_width(), self.grid_size):
            pygame.draw.line(grid_surface, (*self.grid_color, self.grid_alpha), 
                           (x, 0), (x, screen.get_height()))
        for y in range(0, screen.get_height(), self.grid_size):
            pygame.draw.line(grid_surface, (*self.grid_color, self.grid_alpha), 
                           (0, y), (screen.get_width(), y))
        screen.blit(grid_surface, (0, 0))

class LevelManager:
    def __init__(self):
        self.current_level = 1
        self.level = Level(self.current_level)
        self.wave_number = 0
        self.wave_timer = 0
        self.current_pattern = 0
        self.pattern_timer = 0
        self.enemies_spawned = 0
        self.enemies_required = 0
        self.level_complete = False
        self.is_boss_wave = False
        self.boss_spawned = False
        self.waves_per_level = 3
        self.wave_in_progress = False
        self.wave_complete = False
        self.wave_delay = 180  # 3 seconds at 60 FPS

    def update(self, enemy_manager, screen_width, screen_height):
        # If no wave is in progress and we're not waiting for the next wave
        if not self.wave_in_progress and not self.wave_complete:
            self.start_new_wave(enemy_manager, screen_width, screen_height)
            self.wave_in_progress = True
            self.wave_complete = False
        # If wave is in progress, spawn enemies
        elif self.wave_in_progress and not self.wave_complete:
            self.spawn_enemies(enemy_manager, screen_width, screen_height)
            # Check if wave is complete
            if self.enemies_spawned >= self.enemies_required and len(enemy_manager.get_enemies()) == 0:
                self.wave_complete = True
                self.wave_in_progress = False
                self.wave_timer = self.wave_delay  # Start delay timer for next wave

    def start_new_wave(self, enemy_manager, screen_width, screen_height):
        self.wave_number += 1
        self.current_pattern = 0
        self.pattern_timer = 0
        self.enemies_spawned = 0
        
        # Check if this is the boss wave (after 3 regular waves)
        if self.wave_number > self.waves_per_level:
            self.is_boss_wave = True
            self.boss_spawned = False
            self.enemies_required = 1  # Just the boss
        else:
            self.is_boss_wave = False
            # Increase difficulty with each wave
            wave_multiplier = 1 + (self.wave_number - 1) * 0.5
            self.enemies_required = int(sum(pattern["count"] for pattern in self.level.enemy_patterns) * wave_multiplier)

    def spawn_enemies(self, enemy_manager, screen_width, screen_height):
        if self.is_boss_wave:
            if not self.boss_spawned:
                # Spawn the boss in the center
                boss_pos = (screen_width // 2, screen_height // 4)
                enemy_manager.create_enemy(boss_pos, "boss", self.wave_number)
                self.boss_spawned = True
                self.enemies_spawned = 1
            return

        if self.current_pattern >= len(self.level.enemy_patterns):
            return

        pattern = self.level.enemy_patterns[self.current_pattern]
        
        if self.pattern_timer <= 0:
            positions = self.level.get_spawn_positions(
                pattern["formation"],
                pattern["count"],
                screen_width,
                screen_height
            )
            
            for pos in positions:
                enemy_manager.create_enemy(
                    pos,
                    pattern["type"],
                    self.wave_number
                )
                self.enemies_spawned += 1
            
            self.current_pattern += 1
            self.pattern_timer = pattern["spawn_delay"]
        else:
            self.pattern_timer -= 1

    def is_wave_complete(self):
        return self.wave_complete

    def is_level_complete(self):
        """Check if the level is complete (all waves and boss defeated)."""
        return self.wave_number > self.waves_per_level and self.wave_complete

    def get_wave_info(self):
        return {
            "wave": self.wave_number,
            "level": self.current_level,
            "enemies_spawned": self.enemies_spawned,
            "enemies_required": self.enemies_required,
            "is_boss_wave": self.is_boss_wave
        }

    def advance_level(self):
        """Advance to the next level when the player completes the current level."""
        self.current_level = min(3, self.current_level + 1)
        self.level = Level(self.current_level)
        self.wave_number = 0
        self.level_complete = False
        self.is_boss_wave = False
        self.boss_spawned = False
        self.wave_in_progress = False
        self.wave_complete = False

    def reset(self):
        """Reset the level manager to its initial state."""
        self.current_level = 1
        self.level = Level(self.current_level)
        self.wave_number = 0
        self.wave_timer = 0
        self.current_pattern = 0
        self.pattern_timer = 0
        self.enemies_spawned = 0
        self.enemies_required = 0
        self.level_complete = False
        self.is_boss_wave = False
        self.boss_spawned = False
        self.wave_in_progress = False
        self.wave_complete = False 