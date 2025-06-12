"""
Loot management system for handling biome-specific item generation.
"""
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from logger import logger
import json
import hashlib
import os
import pygame
import math

@dataclass
class LootItem:
    """Represents a loot item with its properties."""
    name: str
    rarity: str  # common, uncommon, rare, epic, legendary
    biome_origin: Optional[str]
    effect: Optional[str]
    description: str
    weight: float = 1.0
    # For internal use: effect values, e.g. {'burn': 10}
    effect_values: Dict[str, float] = field(default_factory=dict)

# Path for caching AI-generated loot
AI_LOOT_CACHE_PATH = os.path.join(os.path.dirname(__file__), 'cached_loot.json')

def _load_ai_loot_cache():
    if os.path.exists(AI_LOOT_CACHE_PATH):
        with open(AI_LOOT_CACHE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def _save_ai_loot_cache(cache):
    with open(AI_LOOT_CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)

_ai_loot_cache = _load_ai_loot_cache()

def _ai_cache_key(context: dict) -> str:
    # Use a hash of the context for cache key
    return hashlib.sha256(json.dumps(context, sort_keys=True).encode('utf-8')).hexdigest()

def ai_generate_loot_flavor(context: dict) -> dict:
    """
    Mock AI function for loot flavoring. Replace with real OpenAI/Ollama call as needed.
    Returns a dict with keys: name, description, effect, (optionally more fields).
    """
    # --- MOCKED AI LOGIC ---
    biome = context.get('biome', 'unknown')
    rarity = context.get('rarity', 'common')
    weapon_type = context.get('weapon_type', 'item')
    # Simple flavoring
    name = f"{biome.title()} {rarity.title()} {weapon_type.title()}"
    description = f"A {rarity} {weapon_type} forged in the {biome} biome."
    effect = context.get('effect', None)
    # Add more flavor based on context
    if biome == 'lava' and effect == 'burn':
        description += " It scorches enemies with burning flames."
    elif biome == 'ice' and effect == 'freeze':
        description += " It chills foes to the bone."
    elif biome == 'tech' and effect == 'chain_lightning':
        description += " Unleashes arcs of chain lightning."
    elif biome == 'forest' and effect == 'healing':
        description += " Nature's energy heals the bearer."
    return {
        'name': name,
        'description': description,
        'effect': effect
    }

class LootManager:
    """Manages loot generation and distribution based on biome and difficulty."""
    
    def __init__(self):
        self.items: Dict[str, LootItem] = {}
        self._initialize_items()
        logger.info("Loot manager initialized")
    
    def _initialize_items(self):
        """Initialize all possible loot items."""
        # Common items
        self.items['health_potion'] = LootItem(
            name='Health Potion',
            rarity='common',
            biome_origin=None,
            effect='healing',
            description='Restores 25 health.',
            weight=0.3,
            effect_values={'healing': 25.0}
        )
        self.items['speed_boost'] = LootItem(
            name='Speed Boost',
            rarity='common',
            biome_origin=None,
            effect=None,
            description='Increases speed for a short time.',
            weight=0.2
        )
        # Biome-themed effects
        self.items['ember_orb'] = LootItem(
            name='Ember Orb',
            rarity='uncommon',
            biome_origin='lava',
            effect='burn',
            description='Applies burn to enemies on hit.',
            weight=0.3,
            effect_values={'burn': 10.0}
        )
        self.items['frost_shard'] = LootItem(
            name='Frost Shard',
            rarity='uncommon',
            biome_origin='ice',
            effect='freeze',
            description='Chance to freeze enemies.',
            weight=0.3,
            effect_values={'freeze': 5.0}
        )
        self.items['storm_core'] = LootItem(
            name='Storm Core',
            rarity='rare',
            biome_origin='tech',
            effect='chain_lightning',
            description='Chain lightning on hit.',
            weight=0.2,
            effect_values={'chain_lightning': 15.0}
        )
        self.items['nature_blessing'] = LootItem(
            name='Nature\'s Blessing',
            rarity='rare',
            biome_origin='forest',
            effect='healing',
            description='Heals over time.',
            weight=0.2,
            effect_values={'healing': 10.0}
        )
        # Legendary
        self.items['phoenix_feather'] = LootItem(
            name='Phoenix Feather',
            rarity='legendary',
            biome_origin='lava',
            effect='revive',
            description='Revives the player once upon death.',
            weight=0.1,
            effect_values={'revive': 1.0}
        )
    
    def get_loot_table(self, biome_type: str, difficulty: float) -> Dict[str, float]:
        """Get the loot table for a specific biome and difficulty."""
        loot_table = {}
        for item_name, item in self.items.items():
            if item.biome_origin is None or item.biome_origin == biome_type:
                weight = item.weight * (1.0 + difficulty * 0.5)
                loot_table[item_name] = weight
        return loot_table
    
    def generate_loot(self, biome_type: str, difficulty: float = 0.0, count: int = 1, with_tooltip: bool = False, return_dict: bool = True) -> List:
        """Generate loot items based on biome type and difficulty. Optionally attach tooltip info. Can return dicts or LootItem objects."""
        loot_table = self.get_loot_table(biome_type, difficulty)
        total_weight = sum(loot_table.values())
        if total_weight == 0:
            return []
        normalized_table = {
            name: weight / total_weight
            for name, weight in loot_table.items()
        }
        generated_items = []
        for _ in range(count):
            item_name = random.choices(
                list(normalized_table.keys()),
                weights=list(normalized_table.values())
            )[0]
            item = self.items[item_name]
            if return_dict:
                loot_dict = {
                    'name': item.name,
                    'rarity': item.rarity,
                    'biome_origin': item.biome_origin,
                    'effect': item.effect,
                    'description': item.description,
                    'effect_values': item.effect_values,
                    'weight': item.weight  # Always include weight
                }
                if with_tooltip:
                    loot_dict['tooltip'] = self.generate_tooltip(item)
                generated_items.append(loot_dict)
            else:
                generated_items.append(item)
        return generated_items
    
    def generate_tooltip(self, item: LootItem) -> str:
        """Generate a tooltip string for a loot item."""
        lines = [f"{item.name} [{item.rarity.capitalize()}]"]
        if item.effect:
            lines.append(f"Effect: {item.effect.capitalize()}")
        if item.description:
            lines.append(item.description)
        if item.biome_origin:
            lines.append(f"Origin: {item.biome_origin.capitalize()} biome")
        return "\n".join(lines)
    
    def get_item(self, item_name: str) -> Optional[LootItem]:
        """Get an item by name."""
        return self.items.get(item_name)
    
    def get_items_by_rarity(self, rarity: str) -> List[LootItem]:
        """Get all items of a specific rarity."""
        return [
            item for item in self.items.values()
            if item.rarity == rarity
        ]
    
    def get_biome_items(self, biome_type: str) -> List[LootItem]:
        """Get all items specific to a biome."""
        return [
            item for item in self.items.values()
            if item.biome_origin == biome_type
        ]

    def generate_loot_ai_enhanced(self, biome_type: str, player_stats: dict = None, enemy_types: list = None, recent_loot: list = None, difficulty: float = 0.0, count: int = 1, rarity: str = None) -> list:
        """
        AI-enhanced loot generator (Tier 1-3 ready):
        - Uses base biome + rarity logic
        - Calls AI for name/description/effects
        - Caches results in cached_loot.json
        """
        results = []
        for _ in range(count):
            # 1. Pick a base loot type (weighted random, optionally by rarity)
            loot_table = self.get_loot_table(biome_type, difficulty)
            if rarity:
                loot_table = {k: v for k, v in loot_table.items() if self.items[k].rarity == rarity}
            if not loot_table:
                continue
            total_weight = sum(loot_table.values())
            normalized_table = {k: v / total_weight for k, v in loot_table.items()}
            item_name = random.choices(list(normalized_table.keys()), weights=list(normalized_table.values()))[0]
            base_item = self.items[item_name]
            # 2. Build context for AI
            context = {
                'biome': biome_type,
                'rarity': base_item.rarity,
                'weapon_type': base_item.name.split()[-1].lower(),
                'effect': base_item.effect,
                'player_stats': player_stats or {},
                'enemy_types': enemy_types or [],
                'recent_loot': recent_loot or []
            }
            cache_key = _ai_cache_key(context)
            if cache_key in _ai_loot_cache:
                ai_result = _ai_loot_cache[cache_key]
            else:
                ai_result = ai_generate_loot_flavor(context)
                _ai_loot_cache[cache_key] = ai_result
                _save_ai_loot_cache(_ai_loot_cache)
            # 3. Build the enhanced loot item
            enhanced = {
                'name': ai_result.get('name', base_item.name),
                'rarity': base_item.rarity,
                'biome_origin': biome_type,
                'effect': ai_result.get('effect', base_item.effect),
                'description': ai_result.get('description', base_item.description),
                'effect_values': base_item.effect_values,
                'base_type': base_item.name,
                'ai_context': context
            }
            results.append(enhanced)
        return results

    def update(self, loot_spawns):
        """Stub method to update loot spawns (for compatibility with main loop)."""
        self.loot_spawns = loot_spawns  # Store or process as needed

# Create global instance
loot_manager = LootManager()

# --- Tooltip Renderer (Bonus) ---
import pygame

def render_tooltip(surface: pygame.Surface, text: str, pos: Tuple[int, int], font: Optional[pygame.font.Font] = None, padding: int = 6, color: Tuple[int, int, int] = (30, 30, 30), text_color: Tuple[int, int, int] = (255, 255, 255)):
    """Render a tooltip (text bubble) above loot or on hover."""
    if font is None:
        font = pygame.font.SysFont('arial', 16)
    lines = text.split('\n')
    rendered_lines = [font.render(line, True, text_color) for line in lines]
    width = max(line.get_width() for line in rendered_lines) + 2 * padding
    height = sum(line.get_height() for line in rendered_lines) + 2 * padding
    tooltip_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    tooltip_surf.fill((*color, 220))
    y = padding
    for line in rendered_lines:
        tooltip_surf.blit(line, (padding, y))
        y += line.get_height()
    # Draw border
    pygame.draw.rect(tooltip_surf, (200, 200, 200), tooltip_surf.get_rect(), 2)
    # Blit above the given position
    surface.blit(tooltip_surf, (pos[0] - width // 2, pos[1] - height - 10))
    return tooltip_surf

class LootSprite(pygame.sprite.Sprite):
    """A sprite representing a loot drop in the world."""
    def __init__(self, loot_dict, position, icon_surface=None):
        super().__init__()
        self.loot = loot_dict
        self.base_y = position[1]
        self.hover_phase = 0
        self.hover_amplitude = 6
        self.hover_speed = 0.08
        self.image = icon_surface if icon_surface is not None else self._generate_icon()
        self.rect = self.image.get_rect(center=position)
        self.picked_up = False

    def _generate_icon(self):
        # Simple icon: colored circle with border by rarity
        size = 32
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        rarity_colors = {
            'common': (180, 180, 180),
            'uncommon': (80, 200, 80),
            'rare': (80, 80, 200),
            'epic': (180, 80, 200),
            'legendary': (255, 215, 0)
        }
        border_color = rarity_colors.get(self.loot.get('rarity', 'common'), (180, 180, 180))
        pygame.draw.circle(surf, (40, 40, 40), (size//2, size//2), size//2-2)
        pygame.draw.circle(surf, border_color, (size//2, size//2), size//2-2, 3)
        # Draw effect symbol
        effect = self.loot.get('effect')
        if effect == 'burn':
            pygame.draw.polygon(surf, (255, 80, 0), [(16,8),(24,24),(8,24)])
        elif effect == 'freeze':
            pygame.draw.line(surf, (80,200,255), (16,8), (16,24), 3)
            pygame.draw.line(surf, (80,200,255), (8,16), (24,16), 3)
        elif effect == 'chain_lightning':
            pygame.draw.lines(surf, (200,200,80), False, [(10,10),(22,16),(12,22),(22,28)], 3)
        elif effect == 'healing':
            pygame.draw.line(surf, (80,255,80), (16,10), (16,22), 3)
            pygame.draw.line(surf, (80,255,80), (10,16), (22,16), 3)
        return surf

    def update(self):
        # Hover animation
        self.hover_phase += self.hover_speed
        offset = math.sin(self.hover_phase) * self.hover_amplitude
        self.rect.centery = self.base_y + int(offset)

    def check_pickup(self, player_rect):
        if self.rect.colliderect(player_rect):
            self.picked_up = True
            return True
        return False

def spawn_loot_sprite(loot, position, group, icon_surface=None):
    """Spawn a LootSprite at the given position and add to the group."""
    sprite = LootSprite(loot, position, icon_surface)
    group.add(sprite)
    return sprite 