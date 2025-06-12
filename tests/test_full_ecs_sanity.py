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
from tests.dummy_ui_manager import DummyUIManager

# The following may need to be stubbed if not present
try:
    from combat_system import CombatSystem
except ImportError:
    class CombatSystem:
        def __init__(self, entity_manager): pass
try:
    from physics_system import PhysicsSystem
except ImportError:
    class PhysicsSystem:
        def __init__(self): pass
try:
    from collision_system import CollisionSystem
except ImportError:
    class CollisionSystem:
        def __init__(self): pass

class DummyGame:
    pass

class FullSystemSanityTest(unittest.TestCase):
    def setUp(self):
        # Initialize pygame display for asset loading
        pygame.init()
        pygame.display.set_mode((1, 1))

        # 1️⃣ Entity Manager Smoke
        self.entity_manager = EntityManager()

        # 2️⃣ Asset Manager Smoke
        self.asset_manager = AssetManager.get_instance(asset_dir="assets")
        self.asset_manager.load_all()

        # 3️⃣ Zone Template Loader Smoke
        self.template_loader = ZoneTemplateLoader(
            entity_manager=self.entity_manager,
            zones_dir="configs/zones"  # Updated to use correct path
        )

        # 4️⃣ Core Managers
        self.bullet_manager = BulletManager(self.entity_manager)
        self.enemy_manager = EnemyManager(self.entity_manager)
        self.particle_manager = ParticleManager()
        self.physics_system = PhysicsSystem()
        self.collision_system = CollisionSystem()
        self.combat_system = CombatSystem(self.entity_manager)

        # 6️⃣ Create Player Entity Smoke
        try:
            self.player = Player(entity_manager=self.entity_manager, asset_manager=self.asset_manager)
        except TypeError:
            # Fallback for Player(x, y) signature
            self.player = Player(100, 100)

        # 5️⃣ World Manager Smoke
        self.world_manager = WorldManager(
            asset_manager=self.asset_manager,
            zone_template_loader=self.template_loader,
            chunk_manager=None,  # Stub for now
            camera=None,         # Stub for now
            entity_manager=self.entity_manager,
            bullet_manager=self.bullet_manager,
            enemy_manager=self.enemy_manager,
            player=self.player,
            particle_manager=self.particle_manager
        )

        # 7️⃣ Game State Manager Smoke
        self.game_state_manager = GameStateManager(DummyGame())

    def test_system_sanity(self):
        """Basic smoke test to verify all systems initialize properly."""
        self.assertIsNotNone(self.entity_manager, "Entity Manager failed to initialize")
        self.assertIsNotNone(self.asset_manager, "Asset Manager failed to initialize")
        self.assertIsNotNone(self.template_loader, "Zone Template Loader failed to initialize")
        self.assertIsNotNone(self.world_manager, "World Manager failed to initialize")
        self.assertIsNotNone(self.player, "Player failed to initialize")
        self.assertIsNotNone(self.game_state_manager, "Game State Manager failed to initialize") 