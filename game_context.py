"""
Game context singleton for managing global state and system references.
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from logger import logger

@dataclass
class GameContext:
    """Singleton class to manage global game state and system references."""
    # Core systems
    asset_loader: Optional[Any] = None
    tile_manager: Optional[Any] = None
    biome_manager: Optional[Any] = None
    music_manager: Optional[Any] = None
    loot_manager: Optional[Any] = None
    
    # Game state
    current_biome: str = 'grass'
    current_chunk: int = 0
    current_level: int = 1
    difficulty: float = 1.0
    
    # Player state
    player_health: int = 100
    player_score: int = 0
    player_level: int = 1
    
    # Biome-specific state
    biome_states: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'grass': {'ambient_particles': 'leaves', 'music_theme': 'forest'},
        'lava': {'ambient_particles': 'embers', 'music_theme': 'volcanic'},
        'tech': {'ambient_particles': 'sparks', 'music_theme': 'electronic'},
        'ice': {'ambient_particles': 'snow', 'music_theme': 'arctic'},
        'forest': {'ambient_particles': 'leaves', 'music_theme': 'forest'}
    })
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameContext, cls).__new__(cls)
            logger.info("Game context singleton created")
        return cls._instance
    
    def initialize(self, asset_loader, tile_manager, biome_manager=None, 
                  music_manager=None, loot_manager=None):
        """Initialize the game context with required systems."""
        self.asset_loader = asset_loader
        self.tile_manager = tile_manager
        self.biome_manager = biome_manager
        self.music_manager = music_manager
        self.loot_manager = loot_manager
        logger.info("Game context initialized")
    
    def change_biome(self, new_biome: str) -> None:
        """Change the current biome and update related systems."""
        if new_biome in self.biome_states:
            self.current_biome = new_biome
            # Update music if manager exists
            if self.music_manager:
                self.music_manager.change_theme(self.biome_states[new_biome]['music_theme'])
            logger.info(f"Biome changed to {new_biome}")
        else:
            logger.error(f"Invalid biome: {new_biome}")
    
    def get_biome_state(self, biome: str = None) -> Dict[str, Any]:
        """Get the state for a specific biome or current biome."""
        target_biome = biome or self.current_biome
        return self.biome_states.get(target_biome, {})
    
    def update_player_state(self, health: int = None, score: int = None, level: int = None) -> None:
        """Update player state values."""
        if health is not None:
            self.player_health = health
        if score is not None:
            self.player_score = score
        if level is not None:
            self.player_level = level
        logger.debug(f"Player state updated: health={self.player_health}, "
                    f"score={self.player_score}, level={self.player_level}")
    
    def get_current_ambient_particles(self) -> str:
        """Get the ambient particle type for the current biome."""
        return self.biome_states[self.current_biome]['ambient_particles']
    
    def get_current_music_theme(self) -> str:
        """Get the music theme for the current biome."""
        return self.biome_states[self.current_biome]['music_theme']
    
    def increase_difficulty(self, amount: float = 0.1) -> None:
        """Increase the game difficulty."""
        self.difficulty += amount
        logger.info(f"Difficulty increased to {self.difficulty}")

# Create global instance
game_context = GameContext() 