import unittest
import random
from entities import EntityType
from tests.ecs_mock.entity_manager import MockEntityManager
from tests.ecs_mock.world_manager import MockWorldManager
from tests.ecs_mock.game_state_manager import MockGameStateManager
from tests.ecs_mock.asset_manager import MockAssetManager
from tests.mocks.mock_physics_system import MockPhysicsSystem
from tests.mocks.mock_collision_system import MockCollisionSystem
from tests.mocks.mock_bullet_system import MockBulletSystem
from tests.mocks.mock_ai_system import MockAISystem
from tests.mocks.mock_loot_system import MockLootSystem

class SimulationHarness:
    def __init__(self):
        self.entity_manager = MockEntityManager()
        self.world_manager = MockWorldManager()
        self.state_manager = MockGameStateManager()
        self.asset_manager = MockAssetManager()

        self.physics = MockPhysicsSystem()
        self.collision = MockCollisionSystem()
        self.bullets = MockBulletSystem()
        self.ai = MockAISystem()
        self.loot = MockLootSystem()

    def simulate_spawn_random_entities(self, count):
        for _ in range(count):
            entity = self.entity_manager.create_entity(EntityType.ENEMY)
            transform = type("TransformComponent", (), {"x": random.randint(0, 500), "y": random.randint(0, 500)})
            velocity = type("VelocityComponent", (), {"vx": random.uniform(-5, 5), "vy": random.uniform(-5, 5)})
            entity.add_component(transform)
            entity.add_component(velocity)

    def simulate_random_zone_transitions(self, biomes):
        for biome in biomes:
            zone = self.world_manager.generate_zone(biome)
            self.world_manager.set_current_zone(zone)

    def run_simulation_ticks(self, ticks=100):
        dt = 1  # simulate 1 second per tick
        for _ in range(ticks):
            entities = self.entity_manager.get_all_entities()
            self.physics.update(entities, dt)
            self.bullets.update(entities, dt)
            self.ai.update(entities, dt)
            self.collision.check_collisions(entities)

class TestSimulationRegression(unittest.TestCase):
    def test_full_simulation_run(self):
        harness = SimulationHarness()

        # Randomized full simulation
        harness.simulate_spawn_random_entities(250)
        self.assertEqual(len(harness.entity_manager.get_all_entities()), 250)

        harness.simulate_random_zone_transitions(["forest", "cave", "boss", "volcano"])
        self.assertEqual(harness.world_manager.get_current_zone().biome, "volcano")

        harness.run_simulation_ticks(500)

        # Post-simulation sanity checks
        entities = harness.entity_manager.get_all_entities()
        for entity in entities:
            self.assertTrue(hasattr(entity, "id"))

        print("✅ Full Simulation Regression Passed.") 