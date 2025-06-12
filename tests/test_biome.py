"""
Tests for the biome system.
"""
import unittest
import time
from tests.test_config import (
    init_pygame,
    cleanup_pygame,
    TEST_PARAMS,
    TEST_BIOMES,
    TEST_BIOME_LAYOUTS,
    TEST_BIOME_ENEMIES,
    TEST_BIOME_DECORATIONS,
    assert_biome_properties,
    assert_surface_valid
)
from biome import biome_manager

class TestBiomeSystem(unittest.TestCase):
    """Test cases for the biome system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        init_pygame()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        cleanup_pygame()
    
    def test_biome_initialization(self):
        """Test that all biomes are properly initialized."""
        for biome_name, expected_properties in TEST_BIOMES.items():
            biome = biome_manager.get_biome(biome_name)
            self.assertIsNotNone(biome, f"Biome {biome_name} not found")
            assert_biome_properties(biome.__dict__, expected_properties)
    
    def test_biome_tint(self):
        """Test biome tint color and strength."""
        for biome_name, expected in TEST_BIOMES.items():
            tint_color, tint_strength = biome_manager.get_biome_tint(biome_name)
            self.assertEqual(tint_color, expected['tint_color'])
            self.assertEqual(tint_strength, expected['tint_strength'])
    
    def test_biome_overlay(self):
        """Test biome overlay type."""
        for biome_name, expected in TEST_BIOMES.items():
            overlay = biome_manager.get_biome_overlay(biome_name)
            self.assertEqual(overlay, expected['overlay_type'])
    
    def test_biome_loot_table(self):
        """Test biome loot table generation."""
        for biome_name, expected in TEST_BIOMES.items():
            loot_table = biome_manager.get_biome_loot_table(biome_name)
            self.assertEqual(loot_table, expected['loot_table'])
    
    def test_biome_enemies(self):
        """Test biome enemy types."""
        for biome_name in TEST_BIOMES:
            enemies = biome_manager.get_biome_enemies(biome_name)
            self.assertIsInstance(enemies, list)
            self.assertTrue(len(enemies) > 0)
    
    def test_biome_platforms(self):
        """Test biome platform types."""
        for biome_name in TEST_BIOMES:
            platforms = biome_manager.get_biome_platforms(biome_name)
            self.assertIsInstance(platforms, list)
            self.assertTrue(len(platforms) > 0)
    
    def test_biome_hazards(self):
        """Test biome hazard types."""
        for biome_name in TEST_BIOMES:
            hazards = biome_manager.get_biome_hazards(biome_name)
            self.assertIsInstance(hazards, list)
            self.assertTrue(len(hazards) > 0)
    
    def test_biome_ambient(self):
        """Test biome ambient particles and music theme."""
        for biome_name, expected in TEST_BIOMES.items():
            particles, theme = biome_manager.get_biome_ambient(biome_name)
            self.assertEqual(particles, expected['ambient_particles'])
            self.assertEqual(theme, expected['music_theme'])
    
    def test_biome_visuals(self):
        """Test biome visual properties."""
        for biome_name in TEST_BIOMES:
            bg_color, fog_color, fog_density = biome_manager.get_biome_visuals(biome_name)
            self.assertIsInstance(bg_color, tuple)
            self.assertIsInstance(fog_color, tuple)
            self.assertIsInstance(fog_density, float)
            self.assertTrue(0.0 <= fog_density <= 1.0)
    
    def test_invalid_biome(self):
        """Test handling of invalid biome names."""
        invalid_biome = "nonexistent_biome"
        self.assertIsNone(biome_manager.get_biome(invalid_biome))
        self.assertEqual(biome_manager.get_biome_tint(invalid_biome), ((255, 255, 255), 0.0))
        self.assertIsNone(biome_manager.get_biome_overlay(invalid_biome))
        self.assertEqual(biome_manager.get_biome_loot_table(invalid_biome), {})
        self.assertEqual(biome_manager.get_biome_enemies(invalid_biome), [])
        self.assertEqual(biome_manager.get_biome_platforms(invalid_biome), [])
        self.assertEqual(biome_manager.get_biome_hazards(invalid_biome), [])
        self.assertEqual(biome_manager.get_biome_ambient(invalid_biome), ('none', 'none'))
        self.assertEqual(biome_manager.get_biome_visuals(invalid_biome), ((0, 0, 0), (0, 0, 0), 0.0))

if __name__ == '__main__':
    unittest.main() 