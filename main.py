import pygame
import sys
import math
import random
import os
from pygame.locals import *
from bullets import BulletManager
from rpg_system import Stats, RPGUI
from enemies import EnemyManager, Enemy
from save_system import SaveSystem
from statistics import GameStats
from levels import LevelManager
from level_generator import LevelGenerator
from datetime import datetime
from chunk_system import ChunkManager
from typing import Optional
from game_platform import Platform
from sprite_animator import SpriteAnimator
from player import Player
from tiles import TileManager
from logging_config import logger

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class Game:
    def __init__(self):
        logger.info("Initializing game")
        # Initialize Pygame
        pygame.init()
        
        # Set up the display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bullet Hell Game")
        logger.info(f"Display initialized: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        
        # Initialize managers
        self.bullet_manager = BulletManager(self.bullets)
        self.enemy_manager = EnemyManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        logger.info("Managers initialized")
        
        # Create player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.all_sprites.add(self.player)
        logger.info(f"Player created at position ({SCREEN_WIDTH // 2}, {SCREEN_HEIGHT // 2})")
        
        # Initialize tile manager
        self.tile_manager = TileManager()
        
        # Create platforms using the tile manager
        self._create_platforms()
        
        # Generate initial level
        self._generate_initial_level()
        
        # Set up clock
        self.clock = pygame.time.Clock()
        self.last_time = pygame.time.get_ticks()
        logger.info("Game initialization complete")
        
    def _create_platforms(self):
        """Create platforms using the tile manager."""
        logger.debug("Creating platforms")
        # Ground platform
        ground = self.tile_manager.create_platform(0, self.screen.get_height() - 100, 
                                                 self.screen.get_width(), 100)
        self.platforms.add(ground)
        
        # Platforms
        platform_positions = [
            (100, 400, 200, 32),  # (x, y, width, height)
            (400, 300, 200, 32),
            (700, 200, 200, 32),
            (300, 500, 200, 32),
            (600, 400, 200, 32)
        ]
        
        for x, y, width, height in platform_positions:
            platform = self.tile_manager.create_platform(x, y, width, height)
            self.platforms.add(platform)
        
        # Add some decorative platforms
        decorative_patterns = [
            # Pattern 1: Small decorative platform
            [
                ['tile_3_0', 'tile_4_0'],
                ['tile_3_1', 'tile_4_1']
            ],
            # Pattern 2: Another decorative platform
            [
                ['tile_5_0', 'tile_6_0', 'tile_7_0'],
                ['tile_5_1', 'tile_6_1', 'tile_7_1']
            ]
        ]
        
        decorative_positions = [
            (200, 150),  # (x, y)
            (500, 250)
        ]
        
        for pattern, (x, y) in zip(decorative_patterns, decorative_positions):
            platform = self.tile_manager.create_platform_from_tiles(x, y, pattern)
            self.platforms.add(platform)
            
    def _generate_initial_level(self):
        """Generate the initial level layout."""
        logger.info("Generating initial level")
        # Spawn some enemies
        for _ in range(3):
            self.enemy_manager.spawn_enemy(self.player.rect, self.screen.get_width(), self.screen.get_height())
            
    def update(self):
        """Update game state."""
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Update all sprites
        self.all_sprites.update(mouse_pos, self.platforms, self.bullet_manager, 
                              self.screen.get_width(), self.screen.get_height())
        
        # Update bullet manager
        self.bullet_manager.update()
        
        # Update enemy manager
        self.enemy_manager.update(self.player.rect, self.platforms, self.bullet_manager,
                                self.screen.get_width(), self.screen.get_height())
        
        # Check for collisions
        self._check_collisions()
        
    def _check_collisions(self):
        """Check for collisions between game objects."""
        # Check bullet collisions with enemies
        for bullet in self.bullets:
            enemy_hits = pygame.sprite.spritecollide(bullet, self.enemy_manager.enemies, False)
            for enemy in enemy_hits:
                enemy.take_damage(bullet.damage)
                bullet.kill()
                logger.debug(f"Bullet hit enemy: {enemy.id}, damage: {bullet.damage}")
                
        # Check player collisions with enemies
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemy_manager.enemies, False)
        for enemy in enemy_hits:
            self.player.take_damage(1)
            logger.debug(f"Player took damage from enemy: {enemy.id}, health: {self.player.health}")
            
    def draw(self):
        """Draw everything to the screen."""
        # Fill the background
        self.screen.fill((0, 0, 0))
        
        # Draw all sprites
        self.all_sprites.draw(self.screen)
        self.platforms.draw(self.screen)
        self.enemy_manager.enemies.draw(self.screen)
        self.bullet_manager.draw(self.screen)
        
        # Draw UI elements
        self._draw_ui()
        
        # Update the display
        pygame.display.flip()
        
    def _draw_ui(self):
        """Draw UI elements."""
        # Draw health bar
        health_width = 200
        health_height = 20
        health_x = 10
        health_y = 10
        
        # Background
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (health_x, health_y, health_width, health_height))
        
        # Health
        health_ratio = self.player.health / self.player.max_health
        pygame.draw.rect(self.screen, (255, 0, 0),
                        (health_x, health_y, health_width * health_ratio, health_height))
        
        # Draw wave number
        font = pygame.font.Font(None, 36)
        wave_text = font.render(f"Wave: {self.enemy_manager.wave_number}", True, (255, 255, 255))
        self.screen.blit(wave_text, (self.screen.get_width() - 150, 10))
        
    def run(self):
        """Main game loop."""
        logger.info("Starting game loop")
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logger.info("Game quit requested")
                    running = False
                    
            # Update game state
            self.update()
            
            # Draw everything
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(60)
            
        logger.info("Game loop ended")
        pygame.quit()

if __name__ == "__main__":
    try:
        logger.info("Starting game")
        game = Game()
        game.run()
    except Exception as e:
        logger.error(f"Game crashed with error: {str(e)}", exc_info=True)
    finally:
        logger.info("Game shutdown complete")
        sys.exit() 