import pygame
import pytest
from game_state import GameStateManager, GameState
from ui_manager import UIManager, UIComponent
from entities import Entity, EntityType

class MockGameState(GameState):
    def __init__(self, state_id='test'):
        super().__init__(state_id)
        self.event_handled = False
        self.callbacks["handle_event"] = self.handle_event

    def handle_event(self, event):
        self.event_handled = True
        return None

@pytest.fixture
def ui_manager():
    class DummyEntityManager:
        def create_entity(self, entity_type, element_id=None):
            return Entity(entity_type)
    return UIManager(DummyEntityManager())

@pytest.fixture
def game_state(ui_manager):
    class DummyGame:
        def __init__(self, ui_manager):
            self.ui_manager = ui_manager
    dummy_game = DummyGame(ui_manager)
    manager = GameStateManager(dummy_game)
    test_state = MockGameState()
    manager.add_state('test', test_state)
    manager.set_state('test')
    return manager

def test_ui_blocks_game_state_events(ui_manager, game_state):
    # Create a visible UI panel
    panel = Entity(EntityType.EFFECT)
    ui_component = UIComponent(panel)
    ui_component.visible = True
    panel.add_component(ui_component)
    ui_manager.active_panel = panel

    # Create a test event
    event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
    
    # Game state should not handle input when UI is focused
    result = game_state.handle_event(event)
    assert result is None
    assert not game_state.current_state.event_handled

def test_game_state_handles_events_without_ui(ui_manager, game_state):
    # Ensure no UI panel is active
    ui_manager.active_panel = None
    
    # Create a test event
    event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
    
    # Game state should handle input when UI is inactive
    result = game_state.handle_event(event)
    assert result is None  # handle_event returns None but sets event_handled
    assert game_state.current_state.event_handled

def test_mouse_click_inside_panel_blocked(ui_manager, game_state):
    # Create a visible UI panel
    panel = Entity(EntityType.EFFECT)
    ui_component = UIComponent(panel)
    ui_component.visible = True
    ui_component.position = (0, 0)
    ui_component.size = (200, 200)
    panel.add_component(ui_component)
    ui_manager.active_panel = panel

    # Create a mouse click event inside the panel
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (100, 100)})
    
    # Game state should not handle input when click is inside UI panel
    result = game_state.handle_event(event)
    assert result is None
    assert not game_state.current_state.event_handled

def test_mouse_click_outside_panel_handled(ui_manager, game_state):
    # Create a visible UI panel
    panel = Entity(EntityType.EFFECT)
    ui_component = UIComponent(panel)
    ui_component.visible = True
    ui_component.position = (0, 0)
    ui_component.size = (200, 200)
    panel.add_component(ui_component)
    ui_manager.active_panel = panel

    # Create a mouse click event outside the panel
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (300, 300)})
    
    # Game state should handle input when click is outside UI panel
    result = game_state.handle_event(event)
    assert result is None  # handle_event returns None but sets event_handled
    assert game_state.current_state.event_handled

def test_keyboard_events_with_invisible_panel(ui_manager, game_state):
    # Create an invisible UI panel
    panel = Entity(EntityType.EFFECT)
    ui_component = UIComponent(panel)
    ui_component.visible = False
    panel.add_component(ui_component)
    ui_manager.active_panel = panel

    # Create a test event
    event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
    
    # Game state should handle input when UI panel is invisible
    result = game_state.handle_event(event)
    assert result is None  # handle_event returns None but sets event_handled
    assert game_state.current_state.event_handled

def test_multiple_events_handling(ui_manager, game_state):
    # Create a visible UI panel
    panel = Entity(EntityType.EFFECT)
    ui_component = UIComponent(panel)
    ui_component.visible = True
    panel.add_component(ui_component)
    ui_manager.active_panel = panel

    # Test multiple events
    events = [
        pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE}),
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (100, 100)}),
        pygame.event.Event(pygame.KEYUP, {"key": pygame.K_SPACE})
    ]

    for event in events:
        game_state.current_state.event_handled = False
        result = game_state.handle_event(event)
        assert result is None
        if hasattr(event, "pos") and not ui_manager.is_point_inside_panel(event.pos):
            # Mouse event outside panel should be handled
            assert game_state.current_state.event_handled
        else:
            # Keyboard or mouse inside panel should not be handled
            assert not game_state.current_state.event_handled

    # Remove UI panel and test again
    ui_manager.active_panel = None
    game_state.current_state.event_handled = False

    for event in events:
        result = game_state.handle_event(event)
        assert result is None  # handle_event returns None but sets event_handled
        assert game_state.current_state.event_handled 