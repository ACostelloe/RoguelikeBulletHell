"""
Asset management system.
"""
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
import pygame
import os
import json
import logging
from entities import Entity, Component
from logger import logger
import traceback
from assets.background_tiles import BackgroundTiles

# Create a placeholder image for missing assets
def create_placeholder_image(width: int = 32, height: int = 32) -> pygame.Surface:
    """Create a placeholder image for missing assets.
    
    Args:
        width: Width of the placeholder image
        height: Height of the placeholder image
        
    Returns:
        pygame.Surface: A placeholder image with a checkerboard pattern
    """
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill((255, 0, 255))  # Magenta background
    
    # Draw a checkerboard pattern
    for y in range(0, height, 8):
        for x in range(0, width, 8):
            if (x + y) // 8 % 2 == 0:
                pygame.draw.rect(surface, (0, 0, 0), (x, y, 8, 8))
    
    return surface

@dataclass
class AssetComponent(Component):
    """Component for handling assets."""
    asset_id: str
    asset_type: str
    loaded: bool = False
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "loaded": self.loaded,
            "data": self.data
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssetComponent':
        """Create component from dictionary."""
        return cls(
            asset_id=data["asset_id"],
            asset_type=data["asset_type"],
            loaded=data["loaded"],
            data=data["data"]
        )

class AssetManager:
    """Manages game assets."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls, asset_dir: str = "assets") -> 'AssetManager':
        """Get the singleton instance of AssetManager."""
        if cls._instance is None:
            cls._instance = cls(asset_dir)
        return cls._instance
    
    def __init__(self, asset_dir: str):
        """Initialize the asset manager."""
        if AssetManager._instance is not None:
            raise RuntimeError("AssetManager is a singleton class")
            
        self.logger = logging.getLogger("AssetManager")
        
        if not os.path.exists(asset_dir):
            raise FileNotFoundError(f'Missing assets directory: {asset_dir}')
            
        self.asset_dir = os.path.abspath(asset_dir)
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, Dict[int, pygame.font.Font]] = {}
        self.music: Dict[str, str] = {}
        self.data: Dict[str, Dict[str, Any]] = {}
        self.tiles = None
        
        # Create placeholder images for different sizes
        self.placeholders = {
            (32, 32): create_placeholder_image(32, 32),
            (64, 64): create_placeholder_image(64, 64),
            (128, 128): create_placeholder_image(128, 128)
        }
        
        # Load asset index
        self.load_asset_index()
        AssetManager._instance = self
        
    def get_placeholder_image(self, width: int = 32, height: int = 32) -> pygame.Surface:
        """Get a placeholder image of the specified size.
        
        Args:
            width: Desired width of the placeholder
            height: Desired height of the placeholder
            
        Returns:
            pygame.Surface: A placeholder image
        """
        size = (width, height)
        if size not in self.placeholders:
            self.placeholders[size] = create_placeholder_image(width, height)
        return self.placeholders[size]
        
    def load_asset_index(self) -> None:
        """Load the asset index file."""
        try:
            index_path = os.path.join(self.asset_dir, "index.json")
            if os.path.exists(index_path):
                with open(index_path, "r") as f:
                    self.asset_index = json.load(f)
            else:
                self.logger.warning(f"Asset index not found at {index_path}, creating new index")
                self.asset_index = {
                    "images": {},
                    "sounds": {},
                    "fonts": {},
                    "music": {},
                    "data": {}
                }
                self.save_asset_index()
                
        except Exception as e:
            self.logger.error(f"Error loading asset index: {str(e)}")
            self.logger.error(traceback.format_exc())
            self.asset_index = {
                "images": {},
                "sounds": {},
                "fonts": {},
                "music": {},
                "data": {}
            }
            
    def save_asset_index(self) -> None:
        """Save the asset index file."""
        try:
            index_path = os.path.join(self.asset_dir, "index.json")
            with open(index_path, "w") as f:
                json.dump(self.asset_index, f, indent=4)
                
        except Exception as e:
            logger.error(f"Error saving asset index: {str(e)}")
            logger.error(traceback.format_exc())
            
    def load_image(self, image_id: str, path: str) -> Optional[pygame.Surface]:
        """Load an image asset.
        
        Args:
            image_id: Unique identifier for the image
            path: Path to the image file relative to asset_dir
            
        Returns:
            Optional[pygame.Surface]: The loaded image or a placeholder if loading fails
        """
        try:
            if image_id in self.images:
                return self.images[image_id]
                
            full_path = os.path.join(self.asset_dir, path)
            if not os.path.exists(full_path):
                self.logger.error(f"Image not found: {full_path}")
                return self.get_placeholder_image()
                
            image = pygame.image.load(full_path).convert_alpha()
            self.images[image_id] = image
            self.asset_index["images"][image_id] = path
            self.save_asset_index()
            self.logger.debug(f"Loaded image: {image_id} from {full_path}")
            return image
            
        except Exception as e:
            self.logger.error(f"Error loading image {image_id} from {path}: {str(e)}")
            self.logger.error(traceback.format_exc())
            return self.get_placeholder_image()
            
    def load_sound(self, sound_id: str, path: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound asset."""
        try:
            if sound_id in self.sounds:
                return self.sounds[sound_id]
                
            full_path = os.path.join(self.asset_dir, path)
            if not os.path.exists(full_path):
                logger.error(f"Sound not found: {full_path}")
                return None
                
            sound = pygame.mixer.Sound(full_path)
            self.sounds[sound_id] = sound
            self.asset_index["sounds"][sound_id] = path
            self.save_asset_index()
            return sound
            
        except Exception as e:
            logger.error(f"Error loading sound: {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
    def load_font(self, font_id: str, path: str, size: int) -> Optional[pygame.font.Font]:
        """Load a font asset."""
        try:
            if font_id not in self.fonts:
                self.fonts[font_id] = {}
                
            if size in self.fonts[font_id]:
                return self.fonts[font_id][size]
                
            full_path = os.path.join(self.asset_dir, path)
            if not os.path.exists(full_path):
                logger.error(f"Font not found: {full_path}")
                return None
                
            font = pygame.font.Font(full_path, size)
            self.fonts[font_id][size] = font
            self.asset_index["fonts"][font_id] = path
            self.save_asset_index()
            return font
            
        except Exception as e:
            logger.error(f"Error loading font: {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
    def load_music(self, music_id: str, path: str) -> None:
        """Load a music asset."""
        try:
            full_path = os.path.join(self.asset_dir, path)
            if not os.path.exists(full_path):
                logger.error(f"Music not found: {full_path}")
                return
                
            self.music[music_id] = full_path
            self.asset_index["music"][music_id] = path
            self.save_asset_index()
            
        except Exception as e:
            logger.error(f"Error loading music: {str(e)}")
            logger.error(traceback.format_exc())
            
    def load_data(self, data_id: str, path: str) -> Optional[Dict[str, Any]]:
        """Load a data asset."""
        try:
            if data_id in self.data:
                return self.data[data_id]
                
            full_path = os.path.join(self.asset_dir, path)
            if not os.path.exists(full_path):
                logger.error(f"Data not found: {full_path}")
                return None
                
            with open(full_path, "r") as f:
                data = json.load(f)
                
            self.data[data_id] = data
            self.asset_index["data"][data_id] = path
            self.save_asset_index()
            return data
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
    def get_image(self, image_id: str) -> pygame.Surface:
        """Get an image by ID.
        
        Args:
            image_id: ID of the image to get
            
        Returns:
            pygame.Surface: The requested image or a placeholder if not found
        """
        if image_id not in self.images:
            self.logger.warning(f"Image not found: {image_id}, using placeholder")
            return self.get_placeholder_image()
        return self.images[image_id]
        
    def get_sound(self, sound_id: str) -> Optional[pygame.mixer.Sound]:
        """Get a sound asset."""
        return self.sounds.get(sound_id)
        
    def get_font(self, font_id: str, size: int) -> Optional[pygame.font.Font]:
        """Get a font asset."""
        return self.fonts.get(font_id, {}).get(size)
        
    def get_music(self, music_id: str) -> Optional[str]:
        """Get a music asset."""
        return self.music.get(music_id)
        
    def get_data(self, data_id: str) -> Optional[Dict[str, Any]]:
        """Get a data asset."""
        return self.data.get(data_id)
        
    def unload_image(self, image_id: str) -> None:
        """Unload an image asset."""
        self.images.pop(image_id, None)
        self.asset_index["images"].pop(image_id, None)
        self.save_asset_index()
        
    def unload_sound(self, sound_id: str) -> None:
        """Unload a sound asset."""
        self.sounds.pop(sound_id, None)
        self.asset_index["sounds"].pop(sound_id, None)
        self.save_asset_index()
        
    def unload_font(self, font_id: str) -> None:
        """Unload a font asset."""
        self.fonts.pop(font_id, None)
        self.asset_index["fonts"].pop(font_id, None)
        self.save_asset_index()
        
    def unload_music(self, music_id: str) -> None:
        """Unload a music asset."""
        self.music.pop(music_id, None)
        self.asset_index["music"].pop(music_id, None)
        self.save_asset_index()
        
    def unload_data(self, data_id: str) -> None:
        """Unload a data asset."""
        self.data.pop(data_id, None)
        self.asset_index["data"].pop(data_id, None)
        self.save_asset_index()
        
    def unload_all(self) -> None:
        """Unload all assets."""
        self.images.clear()
        self.sounds.clear()
        self.fonts.clear()
        self.music.clear()
        self.data.clear()
        self.asset_index = {
            "images": {},
            "sounds": {},
            "fonts": {},
            "music": {},
            "data": {}
        }
        self.save_asset_index()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert manager to dictionary."""
        return {
            "asset_dir": self.asset_dir,
            "asset_index": self.asset_index
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssetManager':
        """Create manager from dictionary."""
        manager = cls(data["asset_dir"])
        manager.asset_index = data["asset_index"]
        
        # Load all assets from index
        for image_id, path in manager.asset_index["images"].items():
            manager.load_image(image_id, path)
            
        for sound_id, path in manager.asset_index["sounds"].items():
            manager.load_sound(sound_id, path)
            
        for font_id, path in manager.asset_index["fonts"].items():
            manager.load_font(font_id, path, 12)  # Default size
            
        for music_id, path in manager.asset_index["music"].items():
            manager.load_music(music_id, path)
            
        for data_id, path in manager.asset_index["data"].items():
            manager.load_data(data_id, path)
            
        return manager

    def load_all(self) -> None:
        """Load all assets."""
        try:
            # Load background tiles
            self.tiles = BackgroundTiles(self)
            
            # Load other assets
            for image_id, path in self.asset_index.get("images", {}).items():
                self.load_image(image_id, path)
                
            for sound_id, path in self.asset_index.get("sounds", {}).items():
                self.load_sound(sound_id, path)
                
            for font_id, path in self.asset_index.get("fonts", {}).items():
                self.load_font(font_id, path, 32)  # Default size
                
            for music_id, path in self.asset_index.get("music", {}).items():
                self.load_music(music_id, path)
                
            for data_id, path in self.asset_index.get("data", {}).items():
                self.load_data(data_id, path)
                
            self.load_image("background_zone", "tiles/background_tileset.png")
            
        except Exception as e:
            logger.error(f"Error loading all assets: {str(e)}")
            logger.error(traceback.format_exc())

    def load_background(self) -> None:
        """Load the background tileset."""
        try:
            background_path = os.path.join("assets", "RetroPlatformerTilesets", "Tilesets_Sheet.png")
            if os.path.exists(background_path):
                self.load_image("background", background_path)
                print(f"[ASSET] Loaded background tileset from {background_path}")
            else:
                print(f"[ASSET ERROR] Background tileset not found at {background_path}")
        except Exception as e:
            print(f"[ASSET ERROR] Failed to load background tileset: {e}")

    def verify_all_assets(self) -> Dict[str, List[str]]:
        """Verify that all assets in the index exist.
        
        Returns:
            Dict[str, List[str]]: Dictionary of missing assets by type
        """
        missing_assets = {
            "images": [],
            "sounds": [],
            "fonts": [],
            "music": [],
            "data": []
        }
        
        # Verify images
        for image_id, path in self.asset_index["images"].items():
            full_path = os.path.join(self.asset_dir, path)
            if not os.path.exists(full_path):
                missing_assets["images"].append(f"{image_id}: {full_path}")
                
        # Verify sounds
        for sound_id, path in self.asset_index["sounds"].items():
            full_path = os.path.join(self.asset_dir, path)
            if not os.path.exists(full_path):
                missing_assets["sounds"].append(f"{sound_id}: {full_path}")
                
        # Verify fonts
        for font_id, path in self.asset_index["fonts"].items():
            full_path = os.path.join(self.asset_dir, path)
            if not os.path.exists(full_path):
                missing_assets["fonts"].append(f"{font_id}: {full_path}")
                
        # Verify music
        for music_id, path in self.asset_index["music"].items():
            full_path = os.path.join(self.asset_dir, path)
            if not os.path.exists(full_path):
                missing_assets["music"].append(f"{music_id}: {full_path}")
                
        # Verify data files
        for data_id, path in self.asset_index["data"].items():
            full_path = os.path.join(self.asset_dir, path)
            if not os.path.exists(full_path):
                missing_assets["data"].append(f"{data_id}: {full_path}")
                
        # Log results
        for asset_type, missing in missing_assets.items():
            if missing:
                self.logger.warning(f"Missing {asset_type}:")
                for item in missing:
                    self.logger.warning(f"  - {item}")
            else:
                self.logger.debug(f"All {asset_type} verified")
                
        return missing_assets 

    def cleanup(self):
        """Clean up assets if needed (placeholder)."""
        pass 