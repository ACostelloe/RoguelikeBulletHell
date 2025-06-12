import unittest
from components import (
    TransformComponent,
    VelocityComponent,
    HealthComponent,
    StateComponent,
    LootComponent
)

class DummyEntity:
    id = 1

class TestComponents(unittest.TestCase):
    def test_transform_component(self):
        entity = DummyEntity()
        transform = TransformComponent(entity, 100, 200)
        self.assertEqual(transform.x, 100)
        self.assertEqual(transform.y, 200)

    def test_velocity_component(self):
        entity = DummyEntity()
        velocity = VelocityComponent(entity, 5, -3)
        self.assertEqual(velocity.vx, 5)
        self.assertEqual(velocity.vy, -3)

    def test_health_component(self):
        entity = DummyEntity()
        health = HealthComponent(entity)
        health.max_health = 100
        health.current_health = 50
        self.assertEqual(health.max_health, 100)
        self.assertEqual(health.current_health, 50)

    def test_state_component(self):
        entity = DummyEntity()
        state = StateComponent(entity)
        state.set_state("attacking")
        self.assertEqual(state.current_state, "attacking")

    def test_loot_component(self):
        entity = DummyEntity()
        loot = LootComponent(entity, ["gold", "potion"])
        self.assertIn("gold", loot.loot_table)
        self.assertIn("potion", loot.loot_table) 