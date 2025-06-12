"""
Centralized asset loading system.
"""
import os
import pygame
from typing import Dict, Optional
from logger import logger

class AssetLoader:
    def __init__(self):
        self.platform_tiles: Dict[str, pygame.Surface] = {}
        self.overlays: Dict[str, pygame.Surface] = {}
        self.player_sprites: Dict[str, pygame.Surface] = {}
        self.enemy_sprites: Dict[str, pygame.Surface] = {}
        self.backgrounds: Dict[str, pygame.Surface] = {}
        self.ui_elements: Dict[str, pygame.Surface] = {}
        self.is_initialized = False
        logger.info("Asset loader initialized")

    def load_assets(self) -> None:
        """Load all game assets. Must be called after pygame.display.set_mode()."""
        if not self.is_initialized:
            logger.info("Loading game assets...")
            self._load_platform_tiles()
            self._load_overlays()
            self._load_player_sprites()
            self._load_enemy_sprites()
            self._load_backgrounds()
            self._load_ui_elements()
            self.is_initialized = True
            logger.info("Asset loading complete")
        else:
            logger.warning("Assets already loaded")

    def _load_platform_tiles(self) -> None:
        """Load platform tile textures."""
        platform_path = 'assets/platform_tiles'
        if os.path.exists(platform_path):
            for filename in os.listdir(platform_path):
                if filename.endswith('.png'):
                    name = os.path.splitext(filename)[0]
                    path = os.path.join(platform_path, filename)
                    try:
                        self.platform_tiles[name] = pygame.image.load(path).convert_alpha()
                        logger.debug(f"Loaded platform tile: {name}")
                    except pygame.error as e:
                        logger.error(f"Error loading platform tile {name}: {e}")

    def _load_overlays(self) -> None:
        """Load overlay textures for biome effects."""
        overlay_path = 'assets/overlays'
        if os.path.exists(overlay_path):
            for filename in os.listdir(overlay_path):
                if filename.endswith('.png'):
                    name = os.path.splitext(filename)[0]
                    path = os.path.join(overlay_path, filename)
                    try:
                        self.overlays[name] = pygame.image.load(path).convert_alpha()
                        logger.debug(f"Loaded overlay: {name}")
                    except pygame.error as e:
                        logger.error(f"Error loading overlay {name}: {e}")

    def _load_player_sprites(self) -> None:
        """Load player sprite textures."""
        player_path = 'assets/Player'
        if os.path.exists(player_path):
            for filename in os.listdir(player_path):
                if filename.endswith('.png'):
                    name = os.path.splitext(filename)[0]
                    path = os.path.join(player_path, filename)
                    try:
                        self.player_sprites[name] = pygame.image.load(path).convert_alpha()
                        logger.debug(f"Loaded player sprite: {name}")
                    except pygame.error as e:
                        logger.error(f"Error loading player sprite {name}: {e}")

    def _load_enemy_sprites(self) -> None:
        """Load enemy sprite textures."""
        enemy_path = 'assets/monsters'
        if os.path.exists(enemy_path):
            for filename in os.listdir(enemy_path):
                if filename.endswith('.png'):
                    name = os.path.splitext(filename)[0]
                    path = os.path.join(enemy_path, filename)
                    try:
                        self.enemy_sprites[name] = pygame.image.load(path).convert_alpha()
                        logger.debug(f"Loaded enemy sprite: {name}")
                    except pygame.error as e:
                        logger.error(f"Error loading enemy sprite {name}: {e}")

    def _load_backgrounds(self) -> None:
        """Load background textures."""
        # TODO: Implement background loading
        pass

    def _load_ui_elements(self) -> None:
        """Load UI element textures."""
        # TODO: Implement UI element loading
        pass

    def get_platform_tile(self, name: str) -> Optional[pygame.Surface]:
        """Get a platform tile by name."""
        return self.platform_tiles.get(name)

    def get_overlay(self, name: str) -> Optional[pygame.Surface]:
        """Get an overlay texture by name."""
        return self.overlays.get(name)

    def get_player_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Get a player sprite by name."""
        return self.player_sprites.get(name)

    def get_enemy_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Get an enemy sprite by name."""
        return self.enemy_sprites.get(name)

    def get_background(self, name: str) -> Optional[pygame.Surface]:
        """Get a background texture by name."""
        return self.backgrounds.get(name)

    def get_ui_element(self, name: str) -> Optional[pygame.Surface]:
        """Get a UI element by name."""
        return self.ui_elements.get(name)

# Create global instance
asset_loader = AssetLoader() 