"""
Tests for the loot system.
"""
import unittest
import time
from dataclasses import asdict
from tests.test_config import (
    init_pygame,
    cleanup_pygame,
    TEST_PARAMS,
    TEST_LOOT_TABLES,
    TEST_LOOT_ITEMS,
    assert_loot_properties
)
from loot_manager import loot_manager

class TestLootSystem(unittest.TestCase):
    """Test cases for the loot system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        init_pygame()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        cleanup_pygame()
    
    def test_item_initialization(self):
        """Test that all items are properly initialized."""
        for rarity, items in TEST_LOOT_ITEMS.items():
            for item_name, expected_properties in items.items():
                item = loot_manager.get_item(item_name)
                self.assertIsNotNone(item, f"Item {item_name} not found")
                # Use asdict for LootItem, or dict if already dict
                if hasattr(item, '__dataclass_fields__'):
                    item_dict = asdict(item)
                else:
                    item_dict = item
                assert_loot_properties(item_dict, expected_properties)
    
    def test_loot_table_generation(self):
        """Test loot table generation for different biomes and difficulties."""
        test_biomes = ['grass', 'lava', 'ice', 'tech', 'forest']
        test_difficulties = [0.0, 0.5, 1.0]
        
        for biome in test_biomes:
            for difficulty in test_difficulties:
                loot_table = loot_manager.get_loot_table(biome, difficulty)
                self.assertIsInstance(loot_table, dict)
                self.assertTrue(len(loot_table) > 0)
                
                # Check that weights are positive
                for weight in loot_table.values():
                    self.assertGreater(weight, 0.0)
    
    def test_loot_generation(self):
        """Test loot generation with different parameters."""
        test_biomes = ['grass', 'lava', 'ice', 'tech', 'forest']
        test_difficulties = [0.0, 0.5, 1.0]
        test_counts = [1, 5, 10]
        
        for biome in test_biomes:
            for difficulty in test_difficulties:
                for count in test_counts:
                    # Test both dict and dataclass output
                    items_dict = loot_manager.generate_loot(biome, difficulty, count, return_dict=True)
                    items_obj = loot_manager.generate_loot(biome, difficulty, count, return_dict=False)
                    self.assertEqual(len(items_dict), count)
                    self.assertEqual(len(items_obj), count)
                    for item in items_dict:
                        self.assertIn('name', item)
                        self.assertIn('rarity', item)
                        self.assertIn('biome_origin', item)
                        self.assertIn('effect', item)
                        self.assertIn('description', item)
                        self.assertIn('effect_values', item)
                        self.assertIn('weight', item)
                    for item in items_obj:
                        item_dict = asdict(item)
                        self.assertIn('name', item_dict)
                        self.assertIn('rarity', item_dict)
                        self.assertIn('biome_origin', item_dict)
                        self.assertIn('effect', item_dict)
                        self.assertIn('description', item_dict)
                        self.assertIn('effect_values', item_dict)
                        self.assertIn('weight', item_dict)
    
    def test_biome_specific_items(self):
        """Test that biome-specific items are properly associated."""
        test_biomes = ['grass', 'lava', 'ice', 'tech', 'forest']
        
        for biome in test_biomes:
            items = loot_manager.get_biome_items(biome)
            self.assertIsInstance(items, list)
            
            # Check that all items are specific to the biome
            for item in items:
                if hasattr(item, '__dataclass_fields__'):
                    item_dict = asdict(item)
                else:
                    item_dict = item
                self.assertEqual(item_dict['biome_origin'], biome)
    
    def test_items_by_rarity(self):
        """Test getting items by rarity."""
        test_rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary']
        
        for rarity in test_rarities:
            items = loot_manager.get_items_by_rarity(rarity)
            self.assertIsInstance(items, list)
            
            # Check that all items have the correct rarity
            for item in items:
                if hasattr(item, '__dataclass_fields__'):
                    item_dict = asdict(item)
                else:
                    item_dict = item
                self.assertEqual(item_dict['rarity'], rarity)
    
    def test_invalid_item(self):
        """Test handling of invalid item names."""
        invalid_item = "nonexistent_item"
        self.assertIsNone(loot_manager.get_item(invalid_item))
    
    def test_loot_distribution(self):
        """Test that loot distribution follows expected patterns."""
        biome = 'lava'
        difficulty = 0.5
        iterations = TEST_PARAMS['loot_test_iterations']
        
        # Generate a large number of items
        all_items = []
        for _ in range(iterations):
            items = loot_manager.generate_loot(biome, difficulty, 1, return_dict=True)
            all_items.extend(items)
        
        # Count items by rarity
        rarity_counts = {}
        for item in all_items:
            rarity = item['rarity']
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
        
        # Check that we have items of different rarities
        self.assertTrue(len(rarity_counts) > 0)
        
        # Check that common items are more frequent than rare items
        if 'common' in rarity_counts and 'rare' in rarity_counts:
            self.assertGreater(
                rarity_counts['common'],
                rarity_counts['rare']
            )

if __name__ == '__main__':
    unittest.main() 