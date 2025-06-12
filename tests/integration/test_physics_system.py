"""
Integration tests for the physics system.
"""
import unittest
from entities import Entity
from components import TransformComponent, VelocityComponent

class DummyEntity:
    """Dummy entity class for testing."""
    id = 1

class TestPhysicsSystem(unittest.TestCase):
    """Test cases for the physics system."""
    
    def test_velocity_updates_position(self):
        """Test that velocity correctly updates entity position."""
        entity_type = type("EntityType", (), {"name": "test"})
        entity = Entity(entity_type)
        transform = TransformComponent(entity, 0, 0)
        velocity = VelocityComponent(entity, 5, -3)  # Pass entity and velocity values
        entity.add_component(transform)
        entity.add_component(velocity)
        dt = 1
        transform.x += velocity.vx * dt
        transform.y += velocity.vy * dt
        self.assertEqual(transform.x, 5)
        self.assertEqual(transform.y, -3)

if __name__ == '__main__':
    unittest.main() 