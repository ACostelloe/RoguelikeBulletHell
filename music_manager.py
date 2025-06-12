"""
Music management system for handling biome-specific music and transitions.
"""
import pygame
import random
from typing import Dict, Optional, List
from logger import logger

class MusicManager:
    """Manages music playback and transitions between different biome themes."""
    
    def __init__(self):
        self.current_theme: Optional[str] = None
        self.current_track: Optional[str] = None
        self.music_volume: float = 0.5
        self.fade_time: int = 1000  # milliseconds
        self.theme_tracks: Dict[str, List[str]] = {
            'forest': [
                'forest_theme_1',
                'forest_theme_2',
                'forest_ambient'
            ],
            'volcanic': [
                'volcanic_theme_1',
                'volcanic_theme_2',
                'volcanic_ambient'
            ],
            'electronic': [
                'tech_theme_1',
                'tech_theme_2',
                'tech_ambient'
            ],
            'arctic': [
                'ice_theme_1',
                'ice_theme_2',
                'ice_ambient'
            ]
        }
        self.track_paths: Dict[str, str] = {}
        self._load_tracks()
        logger.info("Music manager initialized")
    
    def _load_tracks(self):
        """Load all music track paths."""
        # Forest theme tracks
        self.track_paths['forest_theme_1'] = 'assets/music/forest/theme_1.ogg'
        self.track_paths['forest_theme_2'] = 'assets/music/forest/theme_2.ogg'
        self.track_paths['forest_ambient'] = 'assets/music/forest/ambient.ogg'
        
        # Volcanic theme tracks
        self.track_paths['volcanic_theme_1'] = 'assets/music/volcanic/theme_1.ogg'
        self.track_paths['volcanic_theme_2'] = 'assets/music/volcanic/theme_2.ogg'
        self.track_paths['volcanic_ambient'] = 'assets/music/volcanic/ambient.ogg'
        
        # Tech theme tracks
        self.track_paths['tech_theme_1'] = 'assets/music/tech/theme_1.ogg'
        self.track_paths['tech_theme_2'] = 'assets/music/tech/theme_2.ogg'
        self.track_paths['tech_ambient'] = 'assets/music/tech/ambient.ogg'
        
        # Ice theme tracks
        self.track_paths['ice_theme_1'] = 'assets/music/ice/theme_1.ogg'
        self.track_paths['ice_theme_2'] = 'assets/music/ice/theme_2.ogg'
        self.track_paths['ice_ambient'] = 'assets/music/ice/ambient.ogg'
    
    def set_volume(self, volume: float):
        """Set the music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        logger.debug(f"Music volume set to {self.music_volume}")
    
    def play_theme(self, theme: str, fade: bool = True):
        """Play a specific biome theme."""
        if theme not in self.theme_tracks:
            logger.warning(f"Unknown theme: {theme}")
            return
        
        if self.current_theme == theme:
            return
        
        # Select a random track from the theme
        available_tracks = self.theme_tracks[theme]
        track = random.choice(available_tracks)
        
        if fade and pygame.mixer.music.get_busy():
            # Fade out current music
            pygame.mixer.music.fadeout(self.fade_time)
            # Wait for fade to complete
            pygame.time.wait(self.fade_time)
        
        try:
            pygame.mixer.music.load(self.track_paths[track])
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.current_theme = theme
            self.current_track = track
            logger.info(f"Playing theme: {theme}, track: {track}")
        except Exception as e:
            logger.error(f"Failed to play music: {e}")
    
    def stop(self, fade: bool = True):
        """Stop the current music."""
        if fade:
            pygame.mixer.music.fadeout(self.fade_time)
        else:
            pygame.mixer.music.stop()
        self.current_theme = None
        self.current_track = None
        logger.info("Music stopped")
    
    def pause(self):
        """Pause the current music."""
        pygame.mixer.music.pause()
        logger.debug("Music paused")
    
    def unpause(self):
        """Unpause the current music."""
        pygame.mixer.music.unpause()
        logger.debug("Music unpaused")
    
    def get_current_theme(self) -> Optional[str]:
        """Get the current theme name."""
        return self.current_theme
    
    def get_current_track(self) -> Optional[str]:
        """Get the current track name."""
        return self.current_track

# Create global instance
music_manager = MusicManager() 