"""
Integration tests for core game systems.
"""
import os
import sys
import unittest
import pygame
import logging
from typing import List, Dict, Any
import traceback

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import init_logger, logger
from asset_manager import AssetManager
from entity_manager import EntityManager
from game_state import GameStateManager
from world_manager import WorldManager
from renderer import Renderer
from entities import Entity, EntityType
from components import (
    TransformComponent,
    SpriteComponent,
    PhysicsComponent,
    CollisionComponent,
    HealthComponent,
    StateComponent
)
from game_state import (
    MenuState,
    PreStartState,
    PlayingState,
    PausedState
)
from zone_template_loader import ZoneTemplateLoader
from chunk_system import ChunkManager
from camera import Camera
from bullets import BulletManager
from enemy_manager import EnemyManager
from particle_system import ParticleManager
from player import Player
from dummy_ui_manager import DummyUIManager

class TestIntegration(unittest.TestCase):
    """Integration tests for core game systems."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Initialize pygame
        pygame.init()
        
        # Initialize logger
        init_logger(
            log_level=logging.DEBUG,
            log_to_file=True,
            log_dir="test_logs",
            show_timestamp=True,
            show_level=True
        )
        
        # Create test window
        cls.screen = pygame.display.set_mode((800, 600))
        cls.clock = pygame.time.Clock()
        
    def setUp(self):
        """Set up each test."""
        try:
            # Only initialize if not already done
            if AssetManager.get_instance() is None:
                self.asset_manager = AssetManager(asset_dir="assets")
            else:
                self.asset_manager = AssetManager.get_instance()
            self.entity_manager = EntityManager()
            class DummyGame: pass
            self.game_state_manager = GameStateManager(DummyGame())
            self.world_manager = build_mock_world()
            self.renderer = Renderer(self.screen, self.entity_manager, self.asset_manager)
            self.asset_manager.load_all()
        except Exception as e:
            print("Exception during setUp:")
            print(e)
            traceback.print_exc()
            raise  # Re-raise so unittest still registers this as failure
        
    def test_asset_verification(self):
        """Test asset verification."""
        logger.info("Testing asset verification...")
        # Verify all assets
        missing_assets = self.asset_manager.verify_all_assets()
        # Check that all lists in missing_assets are empty
        for asset_type, missing in missing_assets.items():
            self.assertEqual(len(missing), 0, f"Missing {asset_type}: {missing}")
        # Verify specific asset types
        self.assertTrue(self.asset_manager.get_image("player") is not None, "Missing player image")
        self.assertTrue(self.asset_manager.get_image("enemies/basic") is not None, "Missing basic enemy image")
        self.assertTrue(self.asset_manager.get_image("tiles/grass") is not None, "Missing grass tile image")
        self.assertTrue(self.asset_manager.get_image("tiles/water") is not None, "Missing water tile image")
        self.assertTrue(self.asset_manager.get_image("ui/heart") is not None, "Missing UI heart image")
        
    def test_entity_management(self):
        """Test entity creation and component management."""
        logger.info("Testing entity management...")
        
        # Create test entity
        entity = Entity(EntityType.PLAYER)
        self.entity_manager.add_entity(entity)
        self.assertIsNotNone(entity, "Failed to create entity")
        
        # Add components
        transform = TransformComponent(entity)
        transform.x = 100
        transform.y = 100
        entity.add_component(transform)
        
        sprite = SpriteComponent(entity)
        sprite.image = self.asset_manager.get_image("player")
        entity.add_component(sprite)
        
        physics = PhysicsComponent(entity)
        physics.mass = 1.0
        physics.friction = 0.1
        entity.add_component(physics)
        
        collision = CollisionComponent(entity)
        collision.width = 32
        collision.height = 32
        entity.add_component(collision)
        
        health = HealthComponent(entity)
        health.max_health = 100
        health.current_health = 100
        entity.add_component(health)
        
        state = StateComponent(entity)
        state.change_state("idle")
        entity.add_component(state)
        
        # Verify component retrieval
        self.assertEqual(entity.get_component(TransformComponent).x, 100)
        self.assertEqual(entity.get_component(TransformComponent).y, 100)
        self.assertIsNotNone(entity.get_component(SpriteComponent).image)
        self.assertEqual(entity.get_component(PhysicsComponent).mass, 1.0)
        self.assertEqual(entity.get_component(CollisionComponent).width, 32)
        self.assertEqual(entity.get_component(HealthComponent).max_health, 100)
        self.assertEqual(entity.get_component(StateComponent).current_state, "idle")
        
        # Test component removal
        entity.remove_component("PhysicsComponent")
        self.assertIsNone(entity.get_component(PhysicsComponent))
        
        # Run audits
        self.entity_manager.run_audits()
        
    def test_state_transitions(self):
        """Test game state transitions."""
        logger.info("Testing state transitions...")
        # Add a stub ui_manager to DummyGame
        class DummyGame:
            def __init__(self):
                self.ui_manager = DummyUIManager()
                self.screen_width = 800
                self.screen_height = 600
        dummy_game = DummyGame()
        self.game_state_manager.add_state("menu", MenuState(dummy_game))
        self.game_state_manager.add_state("prestart", PreStartState(dummy_game))
        self.game_state_manager.add_state("playing", PlayingState(dummy_game))
        self.game_state_manager.add_state("paused", PausedState(dummy_game))
        
        # Test state transitions
        self.game_state_manager.set_state("menu")
        self.assertEqual(self.game_state_manager.current_state.name, "menu")
        
        self.game_state_manager.set_state("prestart")
        self.assertEqual(self.game_state_manager.current_state.name, "prestart")
        
        self.game_state_manager.set_state("playing")
        self.assertEqual(self.game_state_manager.current_state.name, "playing")
        
        self.game_state_manager.push_state("paused")
        self.assertEqual(self.game_state_manager.current_state.name, "paused")
        
        self.game_state_manager.pop_state()
        self.assertEqual(self.game_state_manager.current_state.name, "playing")
        
    def test_world_generation(self):
        """Test world zone generation."""
        logger.info("Testing world generation...")
        # Generate test zones at different coordinates
        self.world_manager._generate_zone(0, 0)
        self.world_manager._generate_zone(1, 0)
        self.world_manager._generate_zone(0, 1)
        zone1 = self.world_manager.zones.get((0, 0))
        zone2 = self.world_manager.zones.get((1, 0))
        zone3 = self.world_manager.zones.get((0, 1))
        self.assertIsNotNone(zone1, "Failed to generate zone at (0, 0)")
        self.assertIsNotNone(zone2, "Failed to generate zone at (1, 0)")
        self.assertIsNotNone(zone3, "Failed to generate zone at (0, 1)")
        # Test zone transitions
        if hasattr(self.world_manager, 'set_current_zone'):
        self.world_manager.set_current_zone(zone1)
        
    def test_render_loop(self):
        """Test renderer with dummy game loop."""
        logger.info("Testing render loop...")
        
        # Create test entities
        player = Entity(EntityType.PLAYER)
        transform = TransformComponent(player)
        transform.x = 400
        transform.y = 300
        player.add_component(transform)
        
        sprite = SpriteComponent(player)
        sprite.image = self.asset_manager.get_image("player")
        player.add_component(sprite)
        
        self.entity_manager.add_entity(player)
        
        # Create a dummy camera
        camera = Camera(800, 600)
        
        # Run dummy game loop
        running = True
        frame_count = 0
        max_frames = 60  # Run for 1 second at 60 FPS
        
        while running and frame_count < max_frames:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            # Update
            self.entity_manager.run_audits()
            
            # Render
            self.renderer.clear()
            self.renderer.render_entities(self.screen, self.entity_manager, camera)
            self.renderer.present()
            
            # Cap frame rate
            self.clock.tick(60)
            frame_count += 1
            
        self.assertEqual(frame_count, max_frames, "Render loop did not complete")
        
    def tearDown(self):
        """Clean up after each test."""
        # Clean up managers
        self.asset_manager.unload_all()
        self.entity_manager = None
        self.game_state_manager = None
        self.world_manager.cleanup()
        self.renderer = None
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        pygame.quit()

def build_mock_world():
    # Create mock or dummy versions of each system
    asset_manager = AssetManager.get_instance()
    if asset_manager is None:
        asset_manager = AssetManager(asset_dir="assets")
    zone_template_loader = ZoneTemplateLoader("tests/zones/")
    chunk_manager = ChunkManager(screen_width=800, screen_height=600)
    camera = Camera(800, 600)
    entity_manager = EntityManager()
    bullet_manager = BulletManager(entity_manager)
    enemy_manager = EnemyManager(entity_manager)
    player = Player(0, 0)
    particle_manager = ParticleManager()

    # Build WorldManager with all dependencies
    world = WorldManager(
        asset_manager,
        zone_template_loader,
        chunk_manager,
        camera,
        entity_manager,
        bullet_manager,
        enemy_manager,
        player,
        particle_manager
    )
    return world

if __name__ == "__main__":
    import traceback
    import sys
    
    class VerboseTestRunner(unittest.TextTestRunner):
        def run(self, test):
            result = super().run(test)
            if not result.wasSuccessful():
                print("\nDetailed error information:")
                for error in result.errors:
                    print("\n" + "="*50)
                    print(error[0])
                    print("-"*50)
                    print(error[1])
                for failure in result.failures:
                    print("\n" + "="*50)
                    print(failure[0])
                    print("-"*50)
                    print(failure[1])
            return result
    
    unittest.main(testRunner=VerboseTestRunner(verbosity=2)) 