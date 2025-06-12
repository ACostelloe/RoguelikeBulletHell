import pygame
import math
from entities import EntityType

def generate_loot_icon(loot):
    size = 32
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    rarity_colors = {
        'common': (180, 180, 180),
        'uncommon': (80, 200, 80),
        'rare': (80, 80, 200),
        'epic': (180, 80, 200),
        'legendary': (255, 215, 0)
    }
    border_color = rarity_colors.get(loot.get('rarity', 'common'), (180, 180, 180))
    pygame.draw.circle(surf, (40, 40, 40), (size//2, size//2), size//2-2)
    pygame.draw.circle(surf, border_color, (size//2, size//2), size//2-2, 3)
    effect = loot.get('effect')
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

class LootSprite(pygame.sprite.Sprite):
    def __init__(self, loot_data, position):
        super().__init__(EntityType.LOOT)
        self.loot = loot_data
        self.image = generate_loot_icon(loot_data)
        self.rect = self.image.get_rect(center=position)
        self.base_y = position[1]
        self.hover_phase = 0
        self.hover_amplitude = 6
        self.hover_speed = 0.08
        self.picked_up = False

    def update(self):
        self.hover_phase += self.hover_speed
        offset = math.sin(self.hover_phase) * self.hover_amplitude
        self.rect.centery = self.base_y + int(offset)

    def pickup(self, player):
        if hasattr(player, 'add_loot'):
            player.add_loot(self.loot)
        elif hasattr(player, 'inventory'):
            player.inventory.append(self.loot)
        self.picked_up = True
        self.kill()

class LootTooltip:
    def __init__(self, loot, font=None):
        self.loot = loot
        self.font = font or pygame.font.SysFont('arial', 18)
        self.title_font = pygame.font.SysFont('arial', 22, bold=True)
        self.surface = self.render_tooltip()

    def render_tooltip(self):
        # Colors by rarity
        rarity_colors = {
            'common': (200, 200, 200),
            'uncommon': (80, 255, 80),
            'rare': (80, 80, 255),
            'epic': (200, 80, 255),
            'legendary': (255, 215, 0)
        }
        rarity = self.loot.get('rarity', 'common')
        name_color = rarity_colors.get(rarity, (200, 200, 200))
        # Tooltip lines
        lines = []
        # Title (larger font)
        lines.append((self.loot.get('name', 'Unknown'), name_color, self.title_font))
        # Separator
        lines.append(('---', (120, 120, 120), self.font))
        # Type/affix
        effect = self.loot.get('effect', 'None')
        effect_color = name_color if effect and effect != 'None' else (180, 180, 180)
        lines.append((f"Type: {effect.capitalize()}", effect_color, self.font))
        # Description
        desc = self.loot.get('description')
        if desc:
            lines.append((desc, (220, 220, 220), self.font))
        # Render lines
        padding = 10
        line_surfs = [f.render(text, True, color) for text, color, f in lines]
        width = max(s.get_width() for s in line_surfs) + 2 * padding
        height = sum(s.get_height() for s in line_surfs) + 2 * padding
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        # Drop shadow
        shadow = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0,0,0,100), (4,4,width-4,height-4), border_radius=8)
        surf.blit(shadow, (0,0))
        # Background
        pygame.draw.rect(surf, (30, 30, 40, 230), (0, 0, width, height), border_radius=8)
        # Border
        pygame.draw.rect(surf, name_color, (0, 0, width, height), 2, border_radius=8)
        # Blit lines
        y = padding
        for idx, s in enumerate(line_surfs):
            surf.blit(s, (padding, y))
            y += s.get_height()
        return surf 