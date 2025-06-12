"""
Input handling system.
"""
from typing import Dict, List, Tuple, Optional, Any, Callable, Set
from dataclasses import dataclass, field
import pygame
from entities import Entity, Component
from logger import logger
import traceback
import time

@dataclass
class InputComponent(Component):
    """Component for handling input."""
    actions: Dict[str, List[int]] = field(default_factory=dict)
    axis: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    callbacks: Dict[str, Callable[[Entity], None]] = field(default_factory=dict)
    last_action_time: Dict[str, float] = field(default_factory=dict)
    
    def add_action(self, name: str, keys: List[int]) -> None:
        """Add an action mapping."""
        self.actions[name] = keys
        logger.debug(f"Added action mapping: {name} -> {keys}")
        
    def add_axis(self, name: str, positive: int, negative: int) -> None:
        """Add an axis mapping."""
        self.axis[name] = (positive, negative)
        logger.debug(f"Added axis mapping: {name} -> ({positive}, {negative})")
        
    def add_callback(self, name: str, callback: Callable[[Entity], None]) -> None:
        """Add a callback for an action."""
        self.callbacks[name] = callback
        logger.debug(f"Added callback for action: {name}")
        
    def remove_action(self, name: str) -> None:
        """Remove an action mapping."""
        self.actions.pop(name, None)
        self.callbacks.pop(name, None)
        logger.debug(f"Removed action mapping: {name}")
        
    def remove_axis(self, name: str) -> None:
        """Remove an axis mapping."""
        self.axis.pop(name, None)
        logger.debug(f"Removed axis mapping: {name}")
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "actions": self.actions,
            "axis": self.axis
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InputComponent':
        """Create component from dictionary."""
        return cls(
            actions=data["actions"],
            axis=data["axis"]
        )

class InputManager:
    """Manages input handling."""
    
    def __init__(self):
        """Initialize the input manager."""
        self.key_state = {}
        self.mouse_pos = (0, 0)
        self.mouse_buttons = (False, False, False)
        self.pressed_keys = set()
        self.last_input_time = time.time()
        self.input_log = []
        self.max_log_size = 1000  # Maximum number of input events to log
        
        # Initialize default key mappings
        self.default_mappings = {
            "move_up": [pygame.K_w],
            "move_down": [pygame.K_s],
            "move_left": [pygame.K_a],
            "move_right": [pygame.K_d],
            "shoot": [pygame.K_SPACE],
            "dash": [pygame.K_LSHIFT],
            "ultimate": [pygame.K_q]
        }
        
        logger.info("InputManager initialized with default mappings")
        
    def update(self):
        """Update input state."""
        try:
            # Update keyboard state
            self.key_state = pygame.key.get_pressed()
            
            # Update mouse state
            self.mouse_pos = pygame.mouse.get_pos()
            self.mouse_buttons = pygame.mouse.get_pressed()
            
            # Log significant input changes
            self._log_input_changes()
            
        except Exception as e:
            logger.error(f"Error updating input: {str(e)}")
            logger.error(traceback.format_exc())
            
    def _log_input_changes(self):
        """Log significant input changes."""
        current_time = time.time()
        
        # Log movement input
        if self.is_pressed(pygame.K_w) or self.is_pressed(pygame.K_s) or \
           self.is_pressed(pygame.K_a) or self.is_pressed(pygame.K_d):
            logger.debug(f"Movement input: W={self.is_pressed(pygame.K_w)}, "
                        f"S={self.is_pressed(pygame.K_s)}, "
                        f"A={self.is_pressed(pygame.K_a)}, "
                        f"D={self.is_pressed(pygame.K_d)}")
            
        # Log attack input
        if self.is_mouse_pressed(0):  # Left mouse button
            logger.debug(f"Attack input at mouse position: {self.mouse_pos}")
            
        # Log ability inputs
        if self.is_pressed(pygame.K_SPACE):
            logger.debug("Dash ability triggered")
        if self.is_pressed(pygame.K_q):
            logger.debug("Ultimate ability triggered")
            
        self.last_input_time = current_time
            
    def is_pressed(self, key):
        """Check if a key is pressed."""
        return self.key_state.get(key, False)
        
    def get_mouse_pos(self):
        """Get the current mouse position."""
        return self.mouse_pos
        
    def is_mouse_pressed(self, button):
        """Check if a mouse button is pressed."""
        return self.mouse_buttons[button]
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a pygame event."""
        try:
            if event.type == pygame.KEYDOWN:
                self.key_state[event.key] = True
                logger.debug(f"Key pressed: {pygame.key.name(event.key)}")
            elif event.type == pygame.KEYUP:
                self.key_state[event.key] = False
                logger.debug(f"Key released: {pygame.key.name(event.key)}")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                logger.debug(f"Mouse button {event.button} pressed at {event.pos}")
            elif event.type == pygame.MOUSEBUTTONUP:
                logger.debug(f"Mouse button {event.button} released at {event.pos}")
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:  # Left mouse button
                    logger.debug(f"Mouse drag at {event.pos}")
                
        except Exception as e:
            logger.error(f"Error handling input event: {str(e)}")
            logger.error(traceback.format_exc())
            
    def is_action_pressed(self, name: str) -> bool:
        """Check if an action is pressed."""
        return self.actions.get(name, False)
        
    def get_axis_value(self, name: str) -> float:
        """Get the value of an axis."""
        return self.axis.get(name, 0.0)
        
    def verify_input_mapping(self, action: str, key: int) -> bool:
        """Verify if an input mapping is valid."""
        if action in self.default_mappings:
            return key in self.default_mappings[action]
        return False
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert manager to dictionary."""
        return {
            "actions": self.actions,
            "axis": self.axis,
            "pressed_keys": list(self.pressed_keys)
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InputManager':
        """Create manager from dictionary."""
        manager = cls()
        manager.actions = data["actions"]
        manager.axis = data["axis"]
        manager.pressed_keys = set(data["pressed_keys"])
        return manager 