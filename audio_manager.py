"""
Audio management system.
"""
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
import pygame
from entities import Entity, Component
from logger import logger
import traceback
from components import TransformComponent

@dataclass
class AudioComponent(Component):
    """Component for handling audio."""
    sound_id: str = ""
    music_id: str = ""
    volume: float = 1.0
    pitch: float = 1.0
    loop: bool = False
    spatial: bool = False
    min_distance: float = 100.0
    max_distance: float = 1000.0
    channel: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "sound_id": self.sound_id,
            "music_id": self.music_id,
            "volume": self.volume,
            "pitch": self.pitch,
            "loop": self.loop,
            "spatial": self.spatial,
            "min_distance": self.min_distance,
            "max_distance": self.max_distance,
            "channel": self.channel
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioComponent':
        """Create component from dictionary."""
        return cls(
            sound_id=data["sound_id"],
            music_id=data["music_id"],
            volume=data["volume"],
            pitch=data["pitch"],
            loop=data["loop"],
            spatial=data["spatial"],
            min_distance=data["min_distance"],
            max_distance=data["max_distance"],
            channel=data["channel"]
        )

class AudioManager:
    """Manages audio playback."""
    
    def __init__(self, asset_manager):
        """Initialize the audio manager."""
        self.asset_manager = asset_manager
        self.music_volume = 1.0
        self.sound_volume = 1.0
        self.master_volume = 1.0
        self.channels: Dict[int, Tuple[Entity, AudioComponent]] = {}
        self.next_channel = 0
        self.max_channels = pygame.mixer.get_num_channels()
        
    def play_sound(self, entity: Entity, sound_id: str, volume: float = 1.0,
                  pitch: float = 1.0, loop: bool = False) -> None:
        """Play a sound effect."""
        try:
            sound = self.asset_manager.get_sound(sound_id)
            if not sound:
                return
                
            # Get or create audio component
            audio = entity.get_component(AudioComponent)
            if not audio:
                audio = AudioComponent()
                entity.add_component(audio)
                
            # Set audio properties
            audio.sound_id = sound_id
            audio.volume = volume
            audio.pitch = pitch
            audio.loop = loop
            
            # Find available channel
            channel = self._get_channel()
            if channel is None:
                return
                
            # Play sound
            sound.set_volume(volume * self.sound_volume * self.master_volume)
            channel.play(sound, loops=-1 if loop else 0)
            
            # Store channel info
            audio.channel = channel
            self.channels[channel] = (entity, audio)
            
        except Exception as e:
            logger.error(f"Error playing sound: {str(e)}")
            logger.error(traceback.format_exc())
            
    def play_music(self, music_id: str, volume: float = 1.0, loop: bool = True) -> None:
        """Play background music."""
        try:
            music_path = self.asset_manager.get_music(music_id)
            if not music_path:
                return
                
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(volume * self.music_volume * self.master_volume)
            pygame.mixer.music.play(loops=-1 if loop else 0)
            
        except Exception as e:
            logger.error(f"Error playing music: {str(e)}")
            logger.error(traceback.format_exc())
            
    def stop_sound(self, entity: Entity) -> None:
        """Stop a sound effect."""
        try:
            audio = entity.get_component(AudioComponent)
            if not audio or audio.channel is None:
                return
                
            channel = audio.channel
            if channel in self.channels:
                channel.stop()
                del self.channels[channel]
                audio.channel = None
                
        except Exception as e:
            logger.error(f"Error stopping sound: {str(e)}")
            logger.error(traceback.format_exc())
            
    def stop_music(self) -> None:
        """Stop background music."""
        try:
            pygame.mixer.music.stop()
            
        except Exception as e:
            logger.error(f"Error stopping music: {str(e)}")
            logger.error(traceback.format_exc())
            
    def pause_sound(self, entity: Entity) -> None:
        """Pause a sound effect."""
        try:
            audio = entity.get_component(AudioComponent)
            if not audio or audio.channel is None:
                return
                
            channel = audio.channel
            if channel in self.channels:
                channel.pause()
                
        except Exception as e:
            logger.error(f"Error pausing sound: {str(e)}")
            logger.error(traceback.format_exc())
            
    def pause_music(self) -> None:
        """Pause background music."""
        try:
            pygame.mixer.music.pause()
            
        except Exception as e:
            logger.error(f"Error pausing music: {str(e)}")
            logger.error(traceback.format_exc())
            
    def unpause_sound(self, entity: Entity) -> None:
        """Unpause a sound effect."""
        try:
            audio = entity.get_component(AudioComponent)
            if not audio or audio.channel is None:
                return
                
            channel = audio.channel
            if channel in self.channels:
                channel.unpause()
                
        except Exception as e:
            logger.error(f"Error unpausing sound: {str(e)}")
            logger.error(traceback.format_exc())
            
    def unpause_music(self) -> None:
        """Unpause background music."""
        try:
            pygame.mixer.music.unpause()
            
        except Exception as e:
            logger.error(f"Error unpausing music: {str(e)}")
            logger.error(traceback.format_exc())
            
    def set_music_volume(self, volume: float) -> None:
        """Set music volume."""
        self.music_volume = max(0.0, min(volume, 1.0))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        
    def set_sound_volume(self, volume: float) -> None:
        """Set sound effects volume."""
        self.sound_volume = max(0.0, min(volume, 1.0))
        for channel, (entity, audio) in self.channels.items():
            sound = self.asset_manager.get_sound(audio.sound_id)
            if sound:
                sound.set_volume(audio.volume * self.sound_volume * self.master_volume)
                
    def set_master_volume(self, volume: float) -> None:
        """Set master volume."""
        self.master_volume = max(0.0, min(volume, 1.0))
        self.set_music_volume(self.music_volume)
        self.set_sound_volume(self.sound_volume)
        
    def update_spatial_audio(self, listener: Entity) -> None:
        """Update spatial audio for all sounds."""
        try:
            listener_transform = listener.get_component(TransformComponent)
            if not listener_transform:
                return
                
            for channel, (entity, audio) in self.channels.items():
                if not audio.spatial:
                    continue
                    
                entity_transform = entity.get_component(TransformComponent)
                if not entity_transform:
                    continue
                    
                # Calculate distance
                dx = entity_transform.x - listener_transform.x
                dy = entity_transform.y - listener_transform.y
                distance = (dx * dx + dy * dy) ** 0.5
                
                # Calculate volume based on distance
                if distance <= audio.min_distance:
                    volume = audio.volume
                elif distance >= audio.max_distance:
                    volume = 0.0
                else:
                    volume = audio.volume * (1.0 - (distance - audio.min_distance) /
                                          (audio.max_distance - audio.min_distance))
                    
                # Update sound volume
                sound = self.asset_manager.get_sound(audio.sound_id)
                if sound:
                    sound.set_volume(volume * self.sound_volume * self.master_volume)
                    
        except Exception as e:
            logger.error(f"Error updating spatial audio: {str(e)}")
            logger.error(traceback.format_exc())
            
    def _get_channel(self) -> Optional[pygame.mixer.Channel]:
        """Get an available audio channel."""
        try:
            # Try to find an available channel
            for i in range(self.max_channels):
                channel = pygame.mixer.Channel(i)
                if not channel.get_busy():
                    return channel
                    
            # If no channel is available, use the next one in round-robin
            channel = pygame.mixer.Channel(self.next_channel)
            self.next_channel = (self.next_channel + 1) % self.max_channels
            return channel
            
        except Exception as e:
            logger.error(f"Error getting audio channel: {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert manager to dictionary."""
        return {
            "music_volume": self.music_volume,
            "sound_volume": self.sound_volume,
            "master_volume": self.master_volume
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], asset_manager) -> 'AudioManager':
        """Create manager from dictionary."""
        manager = cls(asset_manager)
        manager.music_volume = data["music_volume"]
        manager.sound_volume = data["sound_volume"]
        manager.master_volume = data["master_volume"]
        return manager 