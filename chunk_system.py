import pygame
import random
import math
from typing import Dict, List, Tuple, Optional

# Constants
CHUNK_WIDTH = 50  # tiles
CHUNK_HEIGHT = 20  # tiles
TILE_SIZE = 32    # pixels
CHUNK_PIXEL_WIDTH = CHUNK_WIDTH * TILE_SIZE
CHUNK_PIXEL_HEIGHT = CHUNK_HEIGHT * TILE_SIZE

# Camera settings
CAMERA_SMOOTHING = 0.1
CAMERA_LOOK_AHEAD = 0.3  # How far ahead the camera looks in the direction of movement
CAMERA_DEADZONE = 50     # Pixels from center before camera starts moving

# Chunk types
CHUNK_NORMAL = 0
CHUNK_CHALLENGE = 1
CHUNK_SAFE = 2
CHUNK_COLLAPSING = 3

class Camera:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.shake_amount = 0
        self.shake_timer = 0

    def update(self, player_x: float, player_y: float, player_vel_x: float):
        """Update camera position with smooth following and look-ahead."""
        # Calculate target position with look-ahead
        look_ahead_x = player_vel_x * CAMERA_LOOK_AHEAD * 100  # Scale velocity for look-ahead
        self.target_x = player_x - self.screen_width // 2 + look_ahead_x
        self.target_y = player_y - self.screen_height // 2

        # Apply smooth following
        self.x += (self.target_x - self.x) * CAMERA_SMOOTHING
        self.y += (self.target_y - self.y) * CAMERA_SMOOTHING

        # Apply camera shake if active
        if self.shake_timer > 0:
            self.x += random.uniform(-self.shake_amount, self.shake_amount)
            self.y += random.uniform(-self.shake_amount, self.shake_amount)
            self.shake_timer -= 1

    def shake(self, amount: float, duration: int):
        """Apply camera shake effect."""
        self.shake_amount = amount
        self.shake_timer = duration

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates."""
        return (world_x - self.x, world_y - self.y)

    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        return (screen_x + self.x, screen_y + self.y)

class Chunk:
    def __init__(self, chunk_index: int, chunk_width: int, chunk_height: int):
        self.chunk_index = chunk_index
        self.chunk_width = chunk_width
        self.chunk_height = chunk_height
        self.tiles = [[0 for _ in range(chunk_width)] for _ in range(chunk_height)]
        self.platforms = []
        self.enemies = []
        self.items = []
        self.background = None
        self.foreground = None
        self.is_generated = False
        self.enemy_spawn_points = []
        self.powerup_spawn_points = []
        
        # Platform patterns
        self.patterns = [
            [(0, 0), (1, 0), (2, 0)],  # small horizontal
            [(0, 0), (0, 1), (0, 2)],  # vertical shaft
            [(0, 0), (1, 1), (2, 2)]   # stairs up
        ]
        
        # Tile weights for different chunk types
        self.tile_weights = {
            CHUNK_NORMAL: [(2, 0.7), (3, 0.2), (5, 0.1)],  # platform, hazard, unstable
            CHUNK_CHALLENGE: [(2, 0.5), (3, 0.3), (5, 0.2)],  # more hazards
            CHUNK_SAFE: [(2, 0.8), (4, 0.2)],  # platforms and powerups
            CHUNK_COLLAPSING: [(2, 0.3), (5, 0.7)]  # mostly unstable
        }
        
        self.generate()

    def weighted_choice(self, weights):
        """Choose a tile type based on weights."""
        total = sum(w for _, w in weights)
        r = random.uniform(0, total)
        upto = 0
        for tile, w in weights:
            if upto + w >= r:
                return tile
            upto += w
        return weights[0][0]  # Fallback to first option

    def place_pattern(self, pattern, x_start, y_start, tile_type=2):
        """Place a pattern of tiles starting at the given position."""
        for dx, dy in pattern:
            x, y = x_start + dx, y_start + dy
            if 0 <= x < self.chunk_width and 0 <= y < self.chunk_height:
                self.tiles[y][x] = tile_type

    def _generate_normal_chunk(self):
        """Generate a normal chunk layout."""
        # Example: Generate a simple platform layout
        for y in range(self.chunk_height):
            for x in range(self.chunk_width):
                if y > self.chunk_height // 2:  # Bottom half is solid
                    self.tiles[y][x] = 1

    def _generate_challenge_chunk(self):
        """Generate a challenging chunk with more complex patterns."""
        # Generate ground
        for x in range(self.chunk_width):
            self.tiles[self.chunk_height-1][x] = 1

        # Place 4-6 platform patterns
        num_patterns = random.randint(4, 6)
        for _ in range(num_patterns):
            pattern = random.choice(self.patterns)
            x_start = random.randint(0, self.chunk_width - 3)
            y_start = random.randint(3, self.chunk_height - 5)
            
            # Choose tile type based on weights
            tile_type = self.weighted_choice(self.tile_weights[CHUNK_CHALLENGE])
            self.place_pattern(pattern, x_start, y_start, tile_type)

        # Add more enemy spawn points
        for y in range(self.chunk_height):
            for x in range(self.chunk_width):
                if self.tiles[y][x] == 2:
                    if random.random() < 0.4:  # 40% chance for spawn point
                        self.enemy_spawn_points.append((x, y - 1))

    def _generate_safe_chunk(self):
        """Generate a safe chunk with powerups and healing items."""
        # Generate ground
        for x in range(self.chunk_width):
            self.tiles[self.chunk_height-1][x] = 1

        # Place 3-4 platform patterns
        num_patterns = random.randint(3, 4)
        for _ in range(num_patterns):
            pattern = random.choice(self.patterns)
            x_start = random.randint(0, self.chunk_width - 3)
            y_start = random.randint(5, self.chunk_height - 5)
            
            # Choose tile type based on weights
            tile_type = self.weighted_choice(self.tile_weights[CHUNK_SAFE])
            self.place_pattern(pattern, x_start, y_start, tile_type)

        # Add powerup spawn points
        for y in range(self.chunk_height):
            for x in range(self.chunk_width):
                if self.tiles[y][x] == 2:
                    if random.random() < 0.3:  # 30% chance for powerup
                        self.powerup_spawn_points.append((x, y - 1))

    def _generate_collapsing_chunk(self):
        """Generate a collapsing chunk with unstable platforms."""
        # Generate ground
        for x in range(self.chunk_width):
            self.tiles[self.chunk_height-1][x] = 1

        # Place 4-5 platform patterns
        num_patterns = random.randint(4, 5)
        for _ in range(num_patterns):
            pattern = random.choice(self.patterns)
            x_start = random.randint(0, self.chunk_width - 3)
            y_start = random.randint(4, self.chunk_height - 5)
            
            # Choose tile type based on weights
            tile_type = self.weighted_choice(self.tile_weights[CHUNK_COLLAPSING])
            self.place_pattern(pattern, x_start, y_start, tile_type)

        # Add some enemy spawn points
        for y in range(self.chunk_height):
            for x in range(self.chunk_width):
                if self.tiles[y][x] == 2:
                    if random.random() < 0.2:  # 20% chance for spawn point
                        self.enemy_spawn_points.append((x, y - 1))

    def generate(self):
        """Generate the chunk layout."""
        self._generate_normal_chunk()
        self.is_generated = True

class ChunkManager:
    def __init__(self, screen_width: int, screen_height: int):
        self.chunk_width = 800  # Example value, adjust as needed
        self.chunk_height = 600  # Example value, adjust as needed
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.chunks: Dict[int, Chunk] = {}
        self.active_chunks: List[int] = []
        self.camera = Camera(screen_width, screen_height)
        self.left_bound = 0
        self.right_bound = screen_width
        self.shrink_rate = 0.1  # pixels per second
        self.storm_damage = 1
        self.storm_damage_timer = 0
        self.storm_damage_interval = 60  # frames
        self.chunk_load_distance = 2  # Number of chunks to load ahead/behind
        
        # Game progression tracking
        self.time_survived = 0
        self.difficulty_scale = 0.0
        self.landmark_chance = 0.05  # 5% chance for landmark chunks
        
        # Debug visualization
        self.debug_mode = False
        self.debug_colors = {
            2: (150, 150, 150),  # Platform
            3: (255, 0, 0),      # Hazard
            4: (0, 255, 0),      # Powerup
            5: (255, 165, 0)     # Unstable
        }

    def update(self, player_x: float, player_y: float, player_vel_x: float, dt: float) -> bool:
        """Update chunk system and return True if player should take storm damage."""
        # Update time survived and difficulty
        self.time_survived += dt
        self.difficulty_scale = min(1.0, self.time_survived / 300.0)  # Max difficulty after 5 minutes
        
        # Update camera
        self.camera.update(player_x, player_y, player_vel_x)
        
        # Update storm damage
        if self.storm_damage_timer > 0:
            self.storm_damage_timer -= 1
            return False
        
        # Check if player is outside bounds
        if player_x < self.left_bound or player_x > self.right_bound:
            self.storm_damage_timer = self.storm_damage_interval
            return True
        
        # Shrink bounds
        self.left_bound += self.shrink_rate * dt
        self.right_bound -= self.shrink_rate * dt
        
        # Update active chunks
        self._update_active_chunks(player_x)
        
        return False

    def generate_chunk(self, chunk_index):
        """Generate a new chunk at the specified index."""
        chunk = Chunk(chunk_index, self.chunk_width, self.chunk_height)
        chunk._generate_normal_chunk()
        self.chunks[chunk_index] = chunk

    def _update_active_chunks(self, player_x: float):
        """Update which chunks are active based on player position."""
        current_chunk = int(player_x / CHUNK_PIXEL_WIDTH)
        
        # Calculate range of chunks to keep active
        start_chunk = current_chunk - self.chunk_load_distance
        end_chunk = current_chunk + self.chunk_load_distance
        
        # Update active chunks list
        self.active_chunks = list(range(start_chunk, end_chunk + 1))
        
        # Generate new chunks as needed
        for chunk_index in self.active_chunks:
            if chunk_index not in self.chunks:
                self.generate_chunk(chunk_index)

    def get_chunk_at_position(self, x: float, y: float) -> Optional[Chunk]:
        """Get the chunk at the specified world position."""
        chunk_x = int(x // CHUNK_PIXEL_WIDTH)
        return self.chunks.get(chunk_x)

    def draw(self, screen: pygame.Surface):
        """Draw the active chunks and storm bounds."""
        # Draw chunks
        for chunk_index in self.active_chunks:
            if chunk_index in self.chunks:
                chunk = self.chunks[chunk_index]
                self._draw_chunk(screen, chunk)

        # Draw storm bounds
        left_screen_x, _ = self.camera.world_to_screen(self.left_bound, 0)
        right_screen_x, _ = self.camera.world_to_screen(self.right_bound, 0)
        
        pygame.draw.line(screen, (255, 0, 0), 
                        (left_screen_x, 0),
                        (left_screen_x, self.screen_height), 2)
        pygame.draw.line(screen, (255, 0, 0),
                        (right_screen_x, 0),
                        (right_screen_x, self.screen_height), 2)

    def _draw_chunk(self, screen: pygame.Surface, chunk: Chunk):
        """Draw a single chunk's tiles."""
        for y in range(CHUNK_HEIGHT):
            for x in range(CHUNK_WIDTH):
                tile = chunk.tiles[y][x]
                if tile != 0:  # Skip empty tiles
                    world_x = chunk.x_index * CHUNK_PIXEL_WIDTH + x * TILE_SIZE
                    world_y = y * TILE_SIZE
                    screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
                    
                    # Only draw if on screen
                    if (screen_x + TILE_SIZE > 0 and screen_x < self.screen_width and
                        screen_y + TILE_SIZE > 0 and screen_y < self.screen_height):
                        
                        # Draw different tile types
                        if tile == 1:  # Ground
                            pygame.draw.rect(screen, (100, 100, 100),
                                           (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                        elif tile in self.debug_colors:
                            pygame.draw.rect(screen, self.debug_colors[tile],
                                           (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                        
                        # Draw debug overlays
                        if self.debug_mode:
                            # Draw enemy spawn points
                            if (x, y) in chunk.enemy_spawn_points:
                                pygame.draw.circle(screen, (255, 0, 255),
                                                (screen_x + TILE_SIZE//2, screen_y + TILE_SIZE//2), 4)
                            # Draw powerup spawn points
                            if (x, y) in chunk.powerup_spawn_points:
                                pygame.draw.circle(screen, (0, 255, 255),
                                                (screen_x + TILE_SIZE//2, screen_y + TILE_SIZE//2), 4)

    def get_enemy_spawn_points(self, viewport_left: float, viewport_right: float) -> List[Tuple[float, float]]:
        """Get enemy spawn points within the viewport."""
        spawn_points = []
        for chunk_index in self.active_chunks:
            if chunk_index in self.chunks:
                chunk = self.chunks[chunk_index]
                for x, y in chunk.enemy_spawn_points:
                    world_x = chunk_index * CHUNK_PIXEL_WIDTH + x * TILE_SIZE
                    if viewport_left <= world_x <= viewport_right:
                        spawn_points.append((world_x, y * TILE_SIZE))
        return spawn_points

    def get_powerup_spawn_points(self, viewport_left: float, viewport_right: float) -> List[Tuple[float, float]]:
        """Get powerup spawn points within the viewport."""
        spawn_points = []
        for chunk_index in self.active_chunks:
            if chunk_index in self.chunks:
                chunk = self.chunks[chunk_index]
                for x, y in chunk.powerup_spawn_points:
                    world_x = chunk_index * CHUNK_PIXEL_WIDTH + x * TILE_SIZE
                    if viewport_left <= world_x <= viewport_right:
                        spawn_points.append((world_x, y * TILE_SIZE))
        return spawn_points

    def toggle_debug_mode(self):
        """Toggle debug visualization mode."""
        self.debug_mode = not self.debug_mode 