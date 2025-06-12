"""
Tests for the music system.
"""
import unittest
import time
import os
from tests.test_config import (
    init_pygame,
    cleanup_pygame,
    TEST_PARAMS,
    assert_music_playing
)
from music_manager import music_manager

MUSIC_PATHS = [
    'assets/music/forest/theme_1.ogg',
    'assets/music/forest/theme_2.ogg',
    'assets/music/forest/ambient.ogg',
    'assets/music/volcanic/theme_1.ogg',
    'assets/music/volcanic/theme_2.ogg',
    'assets/music/volcanic/ambient.ogg',
    'assets/music/tech/theme_1.ogg',
    'assets/music/tech/theme_2.ogg',
    'assets/music/tech/ambient.ogg',
    'assets/music/ice/theme_1.ogg',
    'assets/music/ice/theme_2.ogg',
    'assets/music/ice/ambient.ogg',
]

def music_files_exist():
    return all(os.path.exists(path) for path in MUSIC_PATHS)

class TestMusicSystem(unittest.TestCase):
    """Test cases for the music system."""
    
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
        # Stop any playing music
        music_manager.stop(fade=False)
    
    def test_theme_initialization(self):
        """Test that all themes are properly initialized."""
        if not music_files_exist():
            self.skipTest("Music files not found. Skipping music tests.")
        test_themes = ['forest', 'volcanic', 'electronic', 'arctic']
        
        for theme in test_themes:
            self.assertIn(theme, music_manager.theme_tracks)
            self.assertTrue(len(music_manager.theme_tracks[theme]) > 0)
    
    def test_track_loading(self):
        """Test that all tracks are properly loaded."""
        if not music_files_exist():
            self.skipTest("Music files not found. Skipping music tests.")
        for theme, tracks in music_manager.theme_tracks.items():
            for track in tracks:
                self.assertIn(track, music_manager.track_paths)
                self.assertTrue(music_manager.track_paths[track].endswith('.ogg'))
    
    def test_volume_control(self):
        """Test volume control functionality."""
        if not music_files_exist():
            self.skipTest("Music files not found. Skipping music tests.")
        test_volumes = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        for volume in test_volumes:
            music_manager.set_volume(volume)
            self.assertEqual(music_manager.music_volume, volume)
    
    def test_theme_playback(self):
        """Test theme playback functionality."""
        if not music_files_exist():
            self.skipTest("Music files not found. Skipping music tests.")
        test_themes = ['forest', 'volcanic', 'electronic', 'arctic']
        
        for theme in test_themes:
            # Play theme
            music_manager.play_theme(theme, fade=False)
            self.assertEqual(music_manager.get_current_theme(), theme)
            self.assertIsNotNone(music_manager.get_current_track())
            self.assertTrue(assert_music_playing(music_manager))
            
            # Stop music
            music_manager.stop(fade=False)
            self.assertIsNone(music_manager.get_current_theme())
            self.assertIsNone(music_manager.get_current_track())
            self.assertFalse(assert_music_playing(music_manager))
    
    def test_theme_transition(self):
        """Test theme transition with fade."""
        if not music_files_exist():
            self.skipTest("Music files not found. Skipping music tests.")
        test_themes = ['forest', 'volcanic', 'electronic', 'arctic']
        
        for i in range(len(test_themes) - 1):
            current_theme = test_themes[i]
            next_theme = test_themes[i + 1]
            
            # Play current theme
            music_manager.play_theme(current_theme, fade=False)
            self.assertEqual(music_manager.get_current_theme(), current_theme)
            
            # Transition to next theme
            music_manager.play_theme(next_theme, fade=True)
            self.assertEqual(music_manager.get_current_theme(), next_theme)
            
            # Wait for fade to complete
            time.sleep(TEST_PARAMS['music_test_duration'])
    
    def test_pause_unpause(self):
        """Test pause and unpause functionality."""
        if not music_files_exist():
            self.skipTest("Music files not found. Skipping music tests.")
        theme = 'forest'
        
        # Play theme
        music_manager.play_theme(theme, fade=False)
        self.assertTrue(assert_music_playing(music_manager))
        
        # Pause
        music_manager.pause()
        self.assertFalse(assert_music_playing(music_manager))
        
        # Unpause
        music_manager.unpause()
        self.assertTrue(assert_music_playing(music_manager))
    
    def test_invalid_theme(self):
        """Test handling of invalid theme names."""
        if not music_files_exist():
            self.skipTest("Music files not found. Skipping music tests.")
        invalid_theme = "nonexistent_theme"
        
        # Try to play invalid theme
        music_manager.play_theme(invalid_theme, fade=False)
        self.assertIsNone(music_manager.get_current_theme())
        self.assertIsNone(music_manager.get_current_track())
        self.assertFalse(assert_music_playing(music_manager))
    
    def test_volume_limits(self):
        """Test volume limit handling."""
        if not music_files_exist():
            self.skipTest("Music files not found. Skipping music tests.")
        # Test below minimum
        music_manager.set_volume(-1.0)
        self.assertEqual(music_manager.music_volume, 0.0)
        
        # Test above maximum
        music_manager.set_volume(2.0)
        self.assertEqual(music_manager.music_volume, 1.0)

if __name__ == '__main__':
    unittest.main() 