import unittest
import pygame
from unittest.mock import Mock, patch

class MockUIComponent:
    def __init__(self, visible=True):
        self.visible = visible
        self.rect = pygame.Rect(100, 100, 200, 200)
        self.callbacks = {}

class MockEntity:
    def __init__(self):
        self.components = {}
        self.type = "EFFECT"
        self.id = "test_entity"

    def add_component(self, component):
        self.components['UI'] = component

    def get_component(self, component_type):
        return self.components.get('UI')

    def has_component(self, component_name):
        return component_name in self.components

class MockUIManager:
    def __init__(self):
        self.elements = {}
        self.active_panel = None

    def has_focus(self):
        return (self.active_panel is not None and 
                self.active_panel.has_component('UI') and 
                self.active_panel.get_component('UI').visible)

    def set_active_panel(self, panel):
        self.active_panel = panel

    def handle_event(self, event):
        if not self.has_focus():
            return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.active_panel:
                ui = self.active_panel.get_component('UI')
                if ui and ui.visible and ui.rect.collidepoint(event.pos):
                    return True
        return False

class TestInputHandling(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.ui_manager = MockUIManager()
        
        # Create test UI panel
        self.panel = MockEntity()
        self.panel.add_component(MockUIComponent())
        
        # Add panel to UI manager
        self.ui_manager.elements["test_panel"] = self.panel
        self.ui_manager.set_active_panel(self.panel)

    def test_ui_focus(self):
        """Test UI focus handling."""
        # Test has_focus
        self.assertTrue(self.ui_manager.has_focus())
        
        # Test focus with invisible panel
        self.panel.get_component('UI').visible = False
        self.assertFalse(self.ui_manager.has_focus())
        
        # Test focus with no active panel
        self.ui_manager.set_active_panel(None)
        self.assertFalse(self.ui_manager.has_focus())

    def test_event_handling(self):
        """Test event handling with UI focus."""
        # Create test events
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
            'pos': (150, 150),  # Inside panel
            'button': 1
        })
        
        outside_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
            'pos': (50, 50),  # Outside panel
            'button': 1
        })
        
        # Test click inside panel
        self.assertTrue(self.ui_manager.handle_event(click_event))
        
        # Test click outside panel
        self.assertFalse(self.ui_manager.handle_event(outside_click))

    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()

if __name__ == '__main__':
    unittest.main() 