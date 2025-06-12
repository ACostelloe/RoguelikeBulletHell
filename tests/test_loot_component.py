"""
Tests for the LootComponent.
"""
import unittest
from components import LootComponent
from tests.test_config import init_pygame, cleanup_pygame

class TestLootComponent(unittest.TestCase):
    """Test cases for the LootComponent."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        init_pygame()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        cleanup_pygame()
    
    def setUp(self):
        """Set up each test case."""
        self.mock_entity = type('MockEntity', (), {'id': 1})()
    
    def test_initialization(self):
        """Test component initialization with and without loot table."""
        # Test with default loot table
        component = LootComponent(self.mock_entity)
        self.assertEqual(component.entity, self.mock_entity)
        self.assertEqual(component.loot_table, [])
        
        # Test with custom loot table
        test_loot = [{'name': 'test_item', 'weight': 1.0}]
        component = LootComponent(self.mock_entity, test_loot)
        self.assertEqual(component.entity, self.mock_entity)
        self.assertEqual(component.loot_table, test_loot)
    
    def test_repr(self):
        """Test string representation of the component."""
        test_loot = [{'name': 'test_item', 'weight': 1.0}]
        component = LootComponent(self.mock_entity, test_loot)
        expected_repr = f"<LootComponent loot_table={test_loot}>"
        self.assertEqual(repr(component), expected_repr)
    
    def test_loot_table_modification(self):
        """Test that loot table can be modified after initialization."""
        component = LootComponent(self.mock_entity)
        test_loot = [{'name': 'test_item', 'weight': 1.0}]
        component.loot_table = test_loot
        self.assertEqual(component.loot_table, test_loot)
    
    def test_empty_loot_table(self):
        """Test behavior with empty loot table."""
        component = LootComponent(self.mock_entity, [])
        self.assertEqual(len(component.loot_table), 0)
        self.assertIsInstance(component.loot_table, list)

if __name__ == '__main__':
    unittest.main() 