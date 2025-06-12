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

        # Inject subsystems
        self.physics = MockPhysicsSystem()
        self.collision = MockCollisionSystem()
        self.bullets = MockBulletSystem()
        self.ai = MockAISystem()
        self.loot = MockLootSystem()

    def simulate_spawn_entities(self, count):
        for _ in range(count):
            entity = self.entity_manager.create_entity(EntityType.ENEMY)
            transform = type("TransformComponent", (), {"x": 0, "y": 0})
            velocity = type("VelocityComponent", (), {"vx": 1, "vy": 0})
            entity.add_component(transform)
            entity.add_component(velocity)

    def simulate_zone_transition(self, biome_list):
        for biome in biome_list:
            zone = self.world_manager.generate_zone(biome)
            self.world_manager.set_current_zone(zone)

    def simulate_state_transitions(self):
        self.state_manager.set_state("menu")
        self.state_manager.push_state("playing")
        self.state_manager.push_state("paused")
        self.state_manager.pop_state()

    def run_simulated_ticks(self, ticks=100):
        dt = 1  # simulate 1 second per tick
        for _ in range(ticks):
            entities = self.entity_manager.get_all_entities()
            self.physics.update(entities, dt)
            self.bullets.update(entities, dt)
            self.ai.update(entities, dt)
            self.collision.check_collisions(entities)

class TestSimulationHarness(unittest.TestCase):
    def test_full_simulation_run(self):
        harness = SimulationHarness()

        harness.simulate_spawn_entities(100)
        self.assertEqual(len(harness.entity_manager.get_all_entities()), 100)

        harness.simulate_zone_transition(["forest", "cave", "boss"])
        self.assertEqual(harness.world_manager.get_current_zone().biome, "boss")

        harness.simulate_state_transitions()
        self.assertEqual(harness.state_manager.current_state.name, "playing")

        harness.run_simulated_ticks(100)

        # Sanity checks
        for entity in harness.entity_manager.get_all_entities():
            self.assertTrue(hasattr(entity, "id"))

        print("Simulation run completed successfully.") 