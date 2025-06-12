"""
Player module.
"""
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
import pygame
import math
import random
from components import SpriteComponent, HealthComponent, TransformComponent
from entities import PhysicsComponent, EntityState
from bullets import Bullet
from powerup import PowerUp
from logger import logger
import traceback
from entities import Entity, EntityType
from pygame.math import Vector2
import os
import json

@dataclass
class PlayerStats:
    """Player statistics and progression."""
    level: int = 1
    experience: float = 0.0
    experience_to_next_level: float = 100.0
    skill_points: int = 0
    score: int = 0
    
    # Base stats
    max_health: float = 100.0
    move_speed: float = 300.0
    attack_speed: float = 1.0
    damage: float = 10.0
    defense: float = 5.0
    
    # Skill levels
    health_level: int = 1
    speed_level: int = 1
    attack_level: int = 1
    defense_level: int = 1
    
    def gain_experience(self, amount: float) -> bool:
        """Gain experience and return True if leveled up."""
        self.experience += amount
        if self.experience >= self.experience_to_next_level:
            self.level_up()
            return True
        return False
        
    def level_up(self) -> None:
        """Handle level up."""
        self.level += 1
        self.experience -= self.experience_to_next_level
        self.experience_to_next_level *= 1.5
        self.skill_points += 1
        
    def upgrade_stat(self, stat_name: str) -> bool:
        """Upgrade a stat if skill points are available."""
        if self.skill_points <= 0:
            return False
            
        stat_level = getattr(self, f"{stat_name}_level", None)
        if stat_level is None:
            return False
            
        setattr(self, f"{stat_name}_level", stat_level + 1)
        self.skill_points -= 1
        
        # Update base stats
        if stat_name == "health":
            self.max_health *= 1.2
        elif stat_name == "speed":
            self.move_speed *= 1.1
        elif stat_name == "attack":
            self.damage *= 1.15
            self.attack_speed *= 1.1
        elif stat_name == "defense":
            self.defense *= 1.2
            
        return True
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "level": self.level,
            "experience": self.experience,
            "experience_to_next_level": self.experience_to_next_level,
            "skill_points": self.skill_points,
            "score": self.score,
            "max_health": self.max_health,
            "move_speed": self.move_speed,
            "attack_speed": self.attack_speed,
            "damage": self.damage,
            "defense": self.defense,
            "health_level": self.health_level,
            "speed_level": self.speed_level,
            "attack_level": self.attack_level,
            "defense_level": self.defense_level
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerStats':
        """Create stats from dictionary."""
        stats = cls()
        for key, value in data.items():
            setattr(stats, key, value)
        return stats

    def update(self, dt):
        pass

@dataclass
class PlayerAbilities:
    """Player abilities and cooldowns."""
    dash_cooldown: float = 0.0
    dash_duration: float = 0.2
    dash_speed: float = 1000.0
    dash_cost: float = 20.0
    
    ultimate_cooldown: float = 0.0
    ultimate_duration: float = 5.0
    ultimate_cost: float = 100.0
    
    is_dashing: bool = False
    is_ultimate_active: bool = False
    
    def update(self, dt: float) -> None:
        """Update ability cooldowns."""
        if self.dash_cooldown > 0:
            self.dash_cooldown = max(0, self.dash_cooldown - dt)
        if self.ultimate_cooldown > 0:
            self.ultimate_cooldown = max(0, self.ultimate_cooldown - dt)
            
    def can_dash(self) -> bool:
        """Check if dash is available."""
        return self.dash_cooldown <= 0
        
    def can_use_ultimate(self) -> bool:
        """Check if ultimate is available."""
        return self.ultimate_cooldown <= 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert abilities to dictionary."""
        return {
            "dash_cooldown": self.dash_cooldown,
            "dash_duration": self.dash_duration,
            "dash_speed": self.dash_speed,
            "dash_cost": self.dash_cost,
            "ultimate_cooldown": self.ultimate_cooldown,
            "ultimate_duration": self.ultimate_duration,
            "ultimate_cost": self.ultimate_cost,
            "is_dashing": self.is_dashing,
            "is_ultimate_active": self.is_ultimate_active
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerAbilities':
        """Create abilities from dictionary."""
        abilities = cls()
        for key, value in data.items():
            setattr(abilities, key, value)
        return abilities

@dataclass
class Item:
    """Base class for items."""
    name: str
    description: str
    item_type: str
    rarity: str = "common"
    level_requirement: int = 1
    stats: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type,
            "rarity": self.rarity,
            "level_requirement": self.level_requirement,
            "stats": self.stats
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """Create item from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"],
            item_type=data["item_type"],
            rarity=data["rarity"],
            level_requirement=data["level_requirement"],
            stats=data["stats"]
        )

class Player(Entity):
    """Player class."""
    
    def __init__(self, x: int, y: int):
        """Initialize player."""
        super().__init__(EntityType.PLAYER)
        
        # Initialize components
        self.add_component(TransformComponent(self, x, y))
        self.add_component(SpriteComponent(self, "player"))
        self.add_component(HealthComponent(self, 100))
        self.add_component(PhysicsComponent(self))
        
        # Initialize player-specific attributes
        self.stats = PlayerStats()
        self.abilities = PlayerAbilities()
        self.inventory = {}
        self.equipped_items = {}
        self.active_effects = set()
        
        # Movement and shooting
        self.move_direction = Vector2(0, 0)
        self.shoot_direction = Vector2(0, 0)
        self.is_shooting = False
        self.last_shot_time = 0
        
        # Load saved data if available
        self._load_player_data()
        
        # Update components with initial stats
        self._update_components()
        
        # Load player sprite
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0))  # Red rectangle for now
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def _load_player_data(self) -> None:
        """Load player data from file."""
        try:
            with open("data/player_data.json", "r") as f:
                data = json.load(f)
                
            # Load stats
            if "stats" in data:
                self.stats = PlayerStats.from_dict(data["stats"])
                
            # Load abilities
            if "abilities" in data:
                self.abilities = PlayerAbilities.from_dict(data["abilities"])
                
            # Load inventory
            if "inventory" in data:
                self.inventory = {name: Item.from_dict(item_data) for name, item_data in data["inventory"].items()}
                
            # Load equipped items
            if "equipped_items" in data:
                self.equipped_items = {type_: Item.from_dict(item_data) for type_, item_data in data["equipped_items"].items()}
                
            # Update components based on loaded data
            self._update_components()
            
        except FileNotFoundError:
            logger.warning("No player data file found. Starting with defaults.")
        except Exception as e:
            logger.error(f"Error loading player data: {str(e)}")
            
    def _save_player_data(self) -> None:
        """Save player data to file."""
        try:
            os.makedirs("data", exist_ok=True)
            data = {
                "stats": self.stats.to_dict(),
                "abilities": self.abilities.to_dict(),
                "inventory": {name: item.to_dict() for name, item in self.inventory.items()},
                "equipped_items": {type_: item.to_dict() for type_, item in self.equipped_items.items()}
            }
            
            with open("data/player_data.json", "w") as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving player data: {str(e)}")
            logger.error(traceback.format_exc())
            
    def _update_components(self) -> None:
        """Update components based on player stats."""
        # Update health component
        health = self.get_component(HealthComponent)
        if health:
            health.max_health = self.stats.max_health
            health.current_health = min(health.current_health, health.max_health)
            
        # Update physics component
        physics = self.get_component(PhysicsComponent)
        if physics:
            physics.mass = 1.0
            physics.friction = 0.1
            
    def handle_input(self, keys, mouse_pos, mouse_buttons):
        """Handle player input."""
        try:
            # Movement
            self.move_direction.x = (keys[pygame.K_d] - keys[pygame.K_a])
            self.move_direction.y = (keys[pygame.K_s] - keys[pygame.K_w])
            if self.move_direction.length() > 0:
                self.move_direction.normalize_ip()
                logger.debug(f"Player movement: {self.move_direction}")
            
            # Shooting
            self.is_shooting = mouse_buttons[0]  # Left mouse button
            if self.is_shooting:
                # Calculate shoot direction from mouse position
                transform = self.get_component(TransformComponent)
                if transform:
                    mouse_x, mouse_y = mouse_pos
                    self.shoot_direction.x = mouse_x - transform.x
                    self.shoot_direction.y = mouse_y - transform.y
                    if self.shoot_direction.length() > 0:
                        self.shoot_direction.normalize_ip()
                        logger.debug(f"Player shooting direction: {self.shoot_direction}")
                    
            # Abilities
            if keys[pygame.K_SPACE] and self.abilities.can_dash():
                logger.info("Player triggered dash ability")
                self._use_dash()
            if keys[pygame.K_r] and self.abilities.can_use_ultimate():
                logger.info("Player triggered ultimate ability")
                self._use_ultimate()
                
        except Exception as e:
            logger.error(f"Error handling player input: {str(e)}")
            logger.error(traceback.format_exc())

    def _use_dash(self) -> None:
        """Use dash ability."""
        if not self.abilities.can_dash():
            logger.debug("Dash ability not available")
            return
            
        self.abilities.is_dashing = True
        self.abilities.dash_cooldown = 1.0  # 1 second cooldown
        
        # Apply dash velocity
        physics = self.get_component(PhysicsComponent)
        if physics:
            physics.velocity_x = self.move_direction.x * self.abilities.dash_speed
            physics.velocity_y = self.move_direction.y * self.abilities.dash_speed
            logger.debug(f"Dash velocity applied: ({physics.velocity_x}, {physics.velocity_y})")
            
    def _use_ultimate(self) -> None:
        """Use ultimate ability."""
        if not self.abilities.can_use_ultimate():
            logger.debug("Ultimate ability not available")
            return
            
        self.abilities.is_ultimate_active = True
        self.abilities.ultimate_cooldown = 30.0  # 30 second cooldown
        
        # Apply ultimate effects
        health = self.get_component(HealthComponent)
        if health:
            health.is_invincible = True
            health.invincibility_time = self.abilities.ultimate_duration
            logger.info("Ultimate ability activated - invincibility granted")
            
    def update(self, dt: float) -> None:
        """Update player state."""
        super().update(dt)
        
        # Update abilities
        self.abilities.update(dt)
        
        # Handle movement
        physics = self.get_component(PhysicsComponent)
        transform = self.get_component(TransformComponent)
        if physics and transform and not self.abilities.is_dashing:
            # Calculate velocity based on move direction
            physics.velocity_x = self.move_direction.x * self.stats.move_speed
            physics.velocity_y = self.move_direction.y * self.stats.move_speed
            
            # Update position based on velocity
            transform.x += physics.velocity_x * dt
            transform.y += physics.velocity_y * dt
            
            # Update rect position to match transform
            self.rect.x = int(transform.x)
            self.rect.y = int(transform.y)
            
        # Handle shooting
        if self.is_shooting:
            current_time = pygame.time.get_ticks() / 1000.0
            if current_time - self.last_shot_time >= 1.0 / self.stats.attack_speed:
                self._shoot()
                self.last_shot_time = current_time
                
        # Update state
        if self.abilities.is_dashing:
            self.state = EntityState.MOVING
        elif self.is_shooting:
            self.state = EntityState.ATTACKING
        elif self.move_direction.length() > 0:
            self.state = EntityState.MOVING
        else:
            self.state = EntityState.IDLE
            
    def add_item(self, item: Item) -> bool:
        """Add an item to inventory."""
        if item.level_requirement > self.stats.level:
            return False
            
        self.inventory[item.name] = item
        self._save_player_data()
        return True
        
    def remove_item(self, item_name: str) -> Optional[Item]:
        """Remove an item from inventory."""
        if item_name in self.inventory:
            item = self.inventory.pop(item_name)
            self._save_player_data()
            return item
        return None
        
    def equip_item(self, item_name: str) -> bool:
        """Equip an item."""
        if item_name not in self.inventory:
            return False
            
        item = self.inventory[item_name]
        if item.level_requirement > self.stats.level:
            return False
            
        # Unequip current item of same type if any
        if item.item_type in self.equipped_items:
            self.unequip_item(item.item_type)
            
        # Equip new item
        self.equipped_items[item.item_type] = item
        
        # Apply item stats
        self._apply_item_stats(item)
        
        self._save_player_data()
        return True
        
    def unequip_item(self, item_type: str) -> Optional[Item]:
        """Unequip an item."""
        if item_type in self.equipped_items:
            item = self.equipped_items.pop(item_type)
            
            # Remove item stats
            self._remove_item_stats(item)
            
            self._save_player_data()
            return item
        return None
        
    def _apply_item_stats(self, item: Item) -> None:
        """Apply item stats to player."""
        for stat_name, value in item.stats.items():
            if hasattr(self.stats, stat_name):
                current_value = getattr(self.stats, stat_name)
                setattr(self.stats, stat_name, current_value + value)
                
        self._update_components()
        
    def _remove_item_stats(self, item: Item) -> None:
        """Remove item stats from player."""
        for stat_name, value in item.stats.items():
            if hasattr(self.stats, stat_name):
                current_value = getattr(self.stats, stat_name)
                setattr(self.stats, stat_name, current_value - value)
                
        self._update_components()
        
    def _shoot(self) -> None:
        """Handle shooting."""
        transform = self.get_component(TransformComponent)
        if not transform:
            logger.error("Cannot shoot: missing TransformComponent")
            return
            
        # Calculate bullet spawn position
        spawn_x = transform.x + self.shoot_direction.x * 20
        spawn_y = transform.y + self.shoot_direction.y * 20
        
        # Create bullet
        bullet = Bullet(
            spawn_x,
            spawn_y,
            self.shoot_direction.x,
            self.shoot_direction.y,
            self.stats.damage
        )
        
        # Add bullet to game world
        if hasattr(self, 'game_world'):
            self.game_world.add_entity(bullet)
            logger.debug(f"Bullet fired at position ({spawn_x}, {spawn_y})")
        else:
            logger.error("Cannot add bullet: game_world not set")
            
    def take_damage(self, amount: float) -> bool:
        """Take damage with defense calculation."""
        if self.abilities.is_ultimate_active:
            return False
            
        # Apply defense reduction
        reduced_amount = max(1, amount - self.stats.defense)
        
        health = self.get_component(HealthComponent)
        if health:
            return health.take_damage(reduced_amount)
        return False
        
    def gain_experience(self, amount: float) -> None:
        """Gain experience and handle level up."""
        if self.stats.gain_experience(amount):
            self._handle_level_up()
            
    def _handle_level_up(self) -> None:
        """Handle level up effects."""
        # Update components
        self._update_components()
        
        # Save player data
        self._save_player_data()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary."""
        data = super().to_dict()
        data.update({
            "stats": self.stats.to_dict(),
            "abilities": self.abilities.to_dict(),
            "inventory": {name: item.to_dict() for name, item in self.inventory.items()},
            "equipped_items": {type_: item.to_dict() for type_, item in self.equipped_items.items()},
            "active_effects": list(self.active_effects)
        })
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create player from dictionary."""
        transform = data["components"]["TransformComponent"]
        player = cls(transform["x"], transform["y"])
        
        # Load player-specific data
        player.stats = PlayerStats.from_dict(data["stats"])
        player.abilities = PlayerAbilities.from_dict(data["abilities"])
        player.inventory = {name: Item.from_dict(item_data) for name, item_data in data["inventory"].items()}
        player.equipped_items = {type_: Item.from_dict(item_data) for type_, item_data in data["equipped_items"].items()}
        player.active_effects = set(data["active_effects"])
        
        # Update components
        player._update_components()
        
        return player 