import pygame
import math

class Stats:
    def __init__(self):
        # Base stats
        self.strength = 1      # Increases bullet damage
        self.agility = 1       # Increases movement speed
        self.vitality = 1      # Increases max health
        self.wisdom = 1        # Reduces cooldowns
        self.luck = 1          # Increases critical hit chance
        
        # Derived stats
        self.max_health = 100
        self.movement_speed = 5
        self.bullet_damage = 10
        self.cooldown_reduction = 0
        self.crit_chance = 0.05  # 5% base crit chance
        
        # Leveling
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100
        self.skill_points = 0
        
        # Update derived stats
        self.update_derived_stats()
    
    def update_derived_stats(self):
        self.max_health = 100 + (self.vitality * 20)
        self.movement_speed = 5 + (self.agility * 0.5)
        self.bullet_damage = 10 + (self.strength * 2)
        self.cooldown_reduction = self.wisdom * 0.05  # 5% reduction per wisdom point
        self.crit_chance = 0.05 + (self.luck * 0.02)  # 2% increase per luck point
    
    def add_experience(self, amount):
        self.experience += amount
        while self.experience >= self.experience_to_next_level:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.experience -= self.experience_to_next_level
        self.experience_to_next_level = int(100 * (1.5 ** (self.level - 1)))
        self.skill_points += 3  # 3 skill points per level
    
    def increase_stat(self, stat_name):
        if self.skill_points > 0:
            if hasattr(self, stat_name):
                setattr(self, stat_name, getattr(self, stat_name) + 1)
                self.skill_points -= 1
                self.update_derived_stats()
                return True
        return False

class RPGUI:
    def __init__(self, stats):
        self.stats = stats
        self.font = pygame.font.Font(None, 32)
        self.show_stats = False
        self.stat_buttons = {}
        self.create_stat_buttons()
    
    def create_stat_buttons(self):
        button_width = 200
        button_height = 40
        start_x = 50
        start_y = 100
        spacing = 50
        
        stats = ['strength', 'agility', 'vitality', 'wisdom', 'luck']
        for i, stat in enumerate(stats):
            self.stat_buttons[stat] = pygame.Rect(
                start_x,
                start_y + (i * spacing),
                button_width,
                button_height
            )
    
    def draw(self, screen):
        if not self.show_stats:
            return
        
        # Draw semi-transparent background
        overlay = pygame.Surface((400, 500))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Draw level and experience
        level_text = self.font.render(f"Level: {self.stats.level}", True, (255, 255, 255))
        exp_text = self.font.render(
            f"XP: {self.stats.experience}/{self.stats.experience_to_next_level}",
            True, (255, 255, 255)
        )
        points_text = self.font.render(
            f"Skill Points: {self.stats.skill_points}",
            True, (255, 255, 255)
        )
        
        screen.blit(level_text, (50, 50))
        screen.blit(exp_text, (200, 50))
        screen.blit(points_text, (50, 400))
        
        # Draw stat buttons
        for stat, rect in self.stat_buttons.items():
            pygame.draw.rect(screen, (100, 100, 100), rect)
            stat_value = getattr(self.stats, stat)
            text = self.font.render(f"{stat.capitalize()}: {stat_value}", True, (255, 255, 255))
            screen.blit(text, (rect.x + 10, rect.y + 5))
    
    def handle_click(self, pos):
        if not self.show_stats:
            return
        
        for stat, rect in self.stat_buttons.items():
            if rect.collidepoint(pos):
                if self.stats.increase_stat(stat):
                    return True
        return False
    
    def toggle_stats(self):
        self.show_stats = not self.show_stats 