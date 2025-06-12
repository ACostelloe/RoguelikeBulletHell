"""
Status effects module.
"""
from typing import Dict, List, Tuple, Optional, Any, Callable, Type
from dataclasses import dataclass, field
from enum import Enum, auto
import pygame
from entities import Entity, Component
from logger import logger
import traceback

class EffectType(Enum):
    """Types of status effects."""
    BUFF = auto()
    DEBUFF = auto()
    DOT = auto()  # Damage over time
    HOT = auto()  # Heal over time
    STUN = auto()
    SLOW = auto()
    SPEED = auto()
    DAMAGE = auto()
    HEAL = auto()
    SHIELD = auto()

@dataclass
class StatusEffect:
    """Base class for status effects."""
    name: str
    effect_type: EffectType
    duration: float
    tick_interval: float = 1.0
    data: Dict[str, Any] = field(default_factory=dict)
    elapsed: float = 0.0
    tick_elapsed: float = 0.0
    
    def update(self, dt: float, entity: Entity) -> bool:
        """Update the effect and return True if it should be removed."""
        self.elapsed += dt
        self.tick_elapsed += dt
        
        if self.tick_elapsed >= self.tick_interval:
            self.tick_elapsed = 0
            self.tick(entity)
            
        return self.elapsed >= self.duration
        
    def tick(self, entity: Entity) -> None:
        """Apply effect tick."""
        pass
        
    def on_apply(self, entity: Entity) -> None:
        """Called when effect is applied."""
        pass
        
    def on_remove(self, entity: Entity) -> None:
        """Called when effect is removed."""
        pass
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert effect to dictionary."""
        return {
            "name": self.name,
            "effect_type": self.effect_type.name,
            "duration": self.duration,
            "tick_interval": self.tick_interval,
            "data": self.data,
            "elapsed": self.elapsed,
            "tick_elapsed": self.tick_elapsed
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StatusEffect':
        """Create effect from dictionary."""
        effect = cls(
            name=data["name"],
            effect_type=EffectType[data["effect_type"]],
            duration=data["duration"],
            tick_interval=data["tick_interval"],
            data=data["data"]
        )
        effect.elapsed = data["elapsed"]
        effect.tick_elapsed = data["tick_elapsed"]
        return effect

@dataclass
class DamageOverTimeEffect(StatusEffect):
    """Damage over time effect."""
    damage_per_tick: float = 0.0
    
    def tick(self, entity: Entity) -> None:
        """Apply damage tick."""
        health = entity.get_component(HealthComponent)
        if health:
            health.take_damage(self.damage_per_tick)
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert effect to dictionary."""
        data = super().to_dict()
        data["damage_per_tick"] = self.damage_per_tick
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DamageOverTimeEffect':
        """Create effect from dictionary."""
        effect = super().from_dict(data)
        effect.damage_per_tick = data["damage_per_tick"]
        return effect

@dataclass
class HealOverTimeEffect(StatusEffect):
    """Heal over time effect."""
    heal_per_tick: float = 0.0
    
    def tick(self, entity: Entity) -> None:
        """Apply heal tick."""
        health = entity.get_component(HealthComponent)
        if health:
            health.heal(self.heal_per_tick)
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert effect to dictionary."""
        data = super().to_dict()
        data["heal_per_tick"] = self.heal_per_tick
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealOverTimeEffect':
        """Create effect from dictionary."""
        effect = super().from_dict(data)
        effect.heal_per_tick = data["heal_per_tick"]
        return effect

@dataclass
class StatModifierEffect(StatusEffect):
    """Stat modifier effect."""
    stat_name: str = ""
    modifier: float = 0.0
    original_value: Optional[float] = None
    
    def on_apply(self, entity: Entity) -> None:
        """Apply stat modifier."""
        if hasattr(entity.stats, self.stat_name):
            self.original_value = getattr(entity.stats, self.stat_name)
            setattr(entity.stats, self.stat_name, self.original_value + self.modifier)
            entity._update_components()
            
    def on_remove(self, entity: Entity) -> None:
        """Remove stat modifier."""
        if self.original_value is not None and hasattr(entity.stats, self.stat_name):
            setattr(entity.stats, self.stat_name, self.original_value)
            entity._update_components()
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert effect to dictionary."""
        data = super().to_dict()
        data.update({
            "stat_name": self.stat_name,
            "modifier": self.modifier,
            "original_value": self.original_value
        })
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StatModifierEffect':
        """Create effect from dictionary."""
        effect = super().from_dict(data)
        effect.stat_name = data["stat_name"]
        effect.modifier = data["modifier"]
        effect.original_value = data["original_value"]
        return effect

@dataclass
class StunEffect(StatusEffect):
    """Stun effect."""
    def on_apply(self, entity: Entity) -> None:
        """Apply stun."""
        entity.state = EntityState.STUNNED
        
    def on_remove(self, entity: Entity) -> None:
        """Remove stun."""
        entity.state = EntityState.IDLE

class StatusEffectManager:
    """Manages status effects for entities."""
    
    def __init__(self):
        """Initialize the effect manager."""
        self.effects: Dict[str, List[StatusEffect]] = {}
        self.effect_types: Dict[str, Type[StatusEffect]] = {
            "DamageOverTimeEffect": DamageOverTimeEffect,
            "HealOverTimeEffect": HealOverTimeEffect,
            "StatModifierEffect": StatModifierEffect,
            "StunEffect": StunEffect
        }
        
    def add_effect(self, entity_id: str, effect: StatusEffect) -> None:
        """Add an effect to an entity."""
        if entity_id not in self.effects:
            self.effects[entity_id] = []
            
        # Check for existing effect of same type
        for existing_effect in self.effects[entity_id]:
            if existing_effect.name == effect.name:
                # Refresh duration
                existing_effect.elapsed = 0
                return
                
        self.effects[entity_id].append(effect)
        
    def remove_effect(self, entity_id: str, effect_name: str) -> None:
        """Remove an effect from an entity."""
        if entity_id in self.effects:
            for effect in self.effects[entity_id]:
                if effect.name == effect_name:
                    self.effects[entity_id].remove(effect)
                    break
                    
    def update(self, dt: float, entity_manager) -> None:
        """Update all effects."""
        for entity_id, effects in list(self.effects.items()):
            entity = entity_manager.get_entity(entity_id)
            if not entity:
                del self.effects[entity_id]
                continue
                
            effects_to_remove = []
            for effect in effects:
                if effect.update(dt, entity):
                    effects_to_remove.append(effect)
                    effect.on_remove(entity)
                    
            for effect in effects_to_remove:
                effects.remove(effect)
                
    def get_effects(self, entity_id: str) -> List[StatusEffect]:
        """Get all effects for an entity."""
        return self.effects.get(entity_id, [])
        
    def has_effect(self, entity_id: str, effect_name: str) -> bool:
        """Check if an entity has a specific effect."""
        if entity_id in self.effects:
            return any(effect.name == effect_name for effect in self.effects[entity_id])
        return False
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert manager to dictionary."""
        return {
            "effects": {
                entity_id: [effect.to_dict() for effect in effects]
                for entity_id, effects in self.effects.items()
            }
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StatusEffectManager':
        """Create manager from dictionary."""
        manager = cls()
        for entity_id, effects_data in data["effects"].items():
            manager.effects[entity_id] = [
                manager.effect_types[effect_data["name"]].from_dict(effect_data)
                for effect_data in effects_data
            ]
        return manager

def create_poison_effect(*args, **kwargs):
    pass

def create_burn_effect(*args, **kwargs):
    pass

def create_freeze_effect(*args, **kwargs):
    pass

def create_stun_effect(*args, **kwargs):
    pass

def create_heal_effect(*args, **kwargs):
    pass

def create_slow_effect(*args, **kwargs):
    pass 