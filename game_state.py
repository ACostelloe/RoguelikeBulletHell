"""
Game state management system.
"""
import pygame
from logger import logger
from entities import TransformComponent
from ui_manager import UIComponent
import time
import traceback

class GameState:
    def __init__(self, state_id):
        self.state_id = state_id
        self.callbacks = {
            "enter": None,
            "exit": None,
            "update": None,
            "render": None,
            "handle_event": None,
        }

    def enter(self):
        if self.callbacks["enter"]:
            self.callbacks["enter"]()

    def exit(self):
        if self.callbacks["exit"]:
            self.callbacks["exit"]()

    def update(self, dt, input_snapshot=None):
        if self.callbacks["update"]:
            self.callbacks["update"](dt, input_snapshot)

    def render(self, surface):
        if self.callbacks["render"]:
            self.callbacks["render"](surface)

    def handle_event(self, event):
        if self.callbacks["handle_event"]:
            self.callbacks["handle_event"](event)

class MenuState(GameState):
    def __init__(self, game):
        super().__init__('menu')
        self.game = game
        self.name = "menu"

    def enter(self):
        print("[MenuState] Entering menu state...")
        self.menu_enter()  # Call menu_enter when entering the state
        super().enter()

    def update(self, dt, input_snapshot=None):
        pass

    def render(self, surface):
        print("[MenuState] Rendering menu...")
        surface.fill((0, 0, 0))
        self.game.ui_manager.render(surface)

    def handle_event(self, event):
        print(f"[MenuState] Handling event: {event}")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            print("[MenuState] ENTER key pressed, transitioning to prestart state")
            self.game.state_manager.set_state("prestart")

    def menu_enter(self):
        print("[MenuState] Setting up menu UI...")
        self.game.ui_manager.focused_element = "menu_instructions"

class PreStartState(GameState):
    def __init__(self, game):
        super().__init__('prestart')
        self.game = game
        self.name = "prestart"

    def enter(self):
        print("[PreStartState] Entering prestart state...")
        self.prestart_enter()
        super().enter()

    def update(self, dt, input_snapshot=None):
        """Update prestart state."""
        # We can use input_snapshot here if needed for any prestart state logic
        pass

    def render(self, surface):
        print("[PreStartState] Rendering prestart...")
        surface.fill((0, 0, 0))
        self.game.ui_manager.render(surface)

    def handle_event(self, event):
        print(f"[PreStartState] Handling event: {event}")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            print("[PreStartState] ENTER key pressed, transitioning to game state")
            self.game.state_manager.set_state("game")

    def prestart_enter(self):
        print("[PreStartState] Setting up prestart UI...")
        # Create prestart panel
        prestart_panel = self.game.ui_manager.create_element(
            "prestart_panel",
            "panel",
            (0, 0),
            (self.game.screen_width, self.game.screen_height),
            style={
                "background_color": (20, 20, 40),
                "border_color": (100, 100, 150),
                "border_width": 2
            }
        )

        # Create continue text
        continue_text = self.game.ui_manager.create_element(
            "prestart_continue",
            "text",
            (0, self.game.screen_height // 2),
            (self.game.screen_width, 50),
            parent="prestart_panel",
            style={
                "font_color": (255, 255, 255),
                "font": pygame.font.Font(None, 36),
                "background_color": (0, 0, 0, 0)
            }
        )

        if continue_text:
            continue_component = continue_text.get_component(UIComponent)
            continue_component.data["text"] = "Press ENTER to Continue"
            continue_component.visible = True
            continue_component.enabled = True

        self.game.ui_manager.focused_element = "prestart_continue"

class PlayingState(GameState):
    def __init__(self, game):
        super().__init__('game')
        self.game = game
        self.name = "playing"
        self.last_input_time = 0
        self.input_cooldown = 0.1  # Minimum time between input processing

    def update(self, dt, input_snapshot=None):
        """Update game state with input handling."""
        try:
            current_time = time.time()
            
            # Process input if cooldown has passed
            if input_snapshot and (current_time - self.last_input_time) >= self.input_cooldown:
                # Handle world input
                self.game.world_manager.handle_input(input_snapshot.keys)
                
                # Handle player input
                self.game.player.handle_input(
                    input_snapshot.keys,
                    input_snapshot.mouse_pos,
                    input_snapshot.mouse_buttons
                )
                
                self.last_input_time = current_time
                logger.debug("Processed input snapshot")
            
            # Update camera
            camera_transform = self.game.camera.get_component(TransformComponent)
            if camera_transform:
                camera_x = camera_transform.x
                camera_y = camera_transform.y
            else:
                camera_x, camera_y = 0, 0
                
            # Update world and chunks
            self.game.world_manager.update(camera_x, camera_y)
            self.game.chunk_manager._update_active_chunks(camera_x)
            
        except Exception as e:
            logger.error(f"Error updating game state: {str(e)}")
            logger.error(traceback.format_exc())

    def render(self, surface):
        self.game.renderer.render_all(
            surface,
            self.game.camera,
            self.game.world_manager,
            self.game.entity_manager,
            self.game.bullet_manager,
            self.game.enemy_manager,
            self.game.ui_manager
        )

    def handle_event(self, event):
        """Handle game events with logging."""
        try:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    logger.info("Pause key pressed, transitioning to pause state")
                    self.game.state_manager.set_state("pause")
                else:
                    logger.debug(f"Gameplay key pressed: {pygame.key.name(event.key)}")
                    self.game.handle_gameplay_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                logger.debug(f"Gameplay mouse button pressed: {event.button} at {event.pos}")
                self.game.handle_gameplay_event(event)
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:  # Left mouse button
                    logger.debug(f"Gameplay mouse drag at {event.pos}")
                    self.game.handle_gameplay_event(event)
                    
        except Exception as e:
            logger.error(f"Error handling game event: {str(e)}")
            logger.error(traceback.format_exc())

class PausedState(GameState):
    def __init__(self, game):
        super().__init__('pause')
        self.game = game
        self.name = "paused"

    def enter(self):
        print("[PausedState] Entering pause state...")
        self.pause_enter()
        super().enter()

    def update(self, dt, input_snapshot=None):
        pass

    def render(self, surface):
        # First render the game state
        self.game.renderer.render_all(
            surface,
            self.game.camera,
            self.game.world_manager,
            self.game.entity_manager,
            self.game.bullet_manager,
            self.game.enemy_manager,
            self.game.ui_manager
        )
        
        # Then add the pause overlay
        overlay = pygame.Surface((self.game.screen_width, self.game.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        surface.blit(overlay, (0, 0))
        
        # Render pause UI
        self.game.ui_manager.render(surface)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                print("[PausedState] P key pressed, returning to game state")
                self.game.state_manager.set_state("game")
            elif event.key == pygame.K_ESCAPE:
                print("[PausedState] ESC key pressed, returning to menu")
                self.game.state_manager.set_state("menu")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle UI element clicks
            self.game.ui_manager.handle_event(event)

    def pause_enter(self):
        print("[PausedState] Setting up pause UI...")
        # Create pause menu panel
        self.game.ui_manager.create_element(
            "pause_menu",
            "panel",
            (self.game.screen_width // 2 - 200, self.game.screen_height // 2 - 150),
            (400, 300),
            style={
                "background_color": (40, 40, 60),
                "border_color": (100, 100, 150),
                "border_width": 2
            }
        )
        
        # Add pause title
        self.game.ui_manager.create_element(
            "pause_title",
            "text",
            (self.game.screen_width // 2 - 100, self.game.screen_height // 2 - 100),
            (200, 50),
            parent="pause_menu",
            style={
                "font": pygame.font.Font(None, 48),
                "font_color": (255, 255, 255)
            }
        )
        
        # Add resume button
        self.game.ui_manager.create_element(
            "resume_button",
            "button",
            (self.game.screen_width // 2 - 80, self.game.screen_height // 2 - 20),
            (160, 30),
            parent="pause_menu",
            style={
                "background_color": (60, 120, 60),
                "border_color": (100, 255, 100),
                "border_width": 1,
                "font": pygame.font.Font(None, 24),
                "font_color": (255, 255, 255)
            }
        )
        
        # Add menu button
        self.game.ui_manager.create_element(
            "menu_button",
            "button",
            (self.game.screen_width // 2 - 80, self.game.screen_height // 2 + 20),
            (160, 30),
            parent="pause_menu",
            style={
                "background_color": (100, 100, 100),
                "border_color": (255, 255, 255),
                "border_width": 1,
                "font": pygame.font.Font(None, 24),
                "font_color": (255, 255, 255)
            }
        )
        
        # Set text for UI elements
        self.game.ui_manager.set_element_text("pause_title", "PAUSED")
        self.game.ui_manager.set_element_text("resume_button", "Resume")
        self.game.ui_manager.set_element_text("menu_button", "Main Menu")
        
        # Set button callbacks
        self.game.ui_manager.set_element_callback("resume_button", lambda: self.game.state_manager.set_state("game"))
        self.game.ui_manager.set_element_callback("menu_button", lambda: self.game.state_manager.set_state("menu"))

class GameStateManager:
    """Manages game states and transitions."""
    
    def __init__(self, game):
        """Initialize the game state manager."""
        self.states = {}
        self.current_state = None
        self.game = game
        self.state_stack = []  # Use a stack for state management
        logger.info("GameStateManager initialized")
        
    def add_state(self, state_id: str, state: GameState):
        """Add a state to the manager."""
        self.states[state_id] = state
        state.manager = self
        logger.info(f"Added state: {state_id}")
        
    def set_state(self, state_id: str):
        print(f"[GameStateManager] set_state called: {state_id}")
        if state_id not in self.states:
            logger.error(f"State {state_id} not found")
            return
        prev = self.current_state.state_id if self.current_state else None
        print(f"[GameStateManager] Transitioning from {prev} to {state_id}")
        if self.current_state:
            self.current_state.exit()
        self.state_stack = [self.states[state_id]]  # Clear stack and set new state
        self.current_state = self.states[state_id]
        print(f"[GameStateManager] State change: {prev} -> {state_id}")
        self.current_state.enter()
        
    def push_state(self, state_id: str):
        """Push a new state onto the stack."""
        if state_id not in self.states:
            logger.error(f"State {state_id} not found")
            return
        if self.current_state:
            self.current_state.exit()
        self.state_stack.append(self.states[state_id])
        self.current_state = self.states[state_id]
        logger.info(f"State push: {state_id}")
        self.current_state.enter()
        
    def pop_state(self):
        """Pop the current state and return to the previous state (safe)."""
        if self.state_stack:
            self.current_state = self.state_stack.pop()
            logger.info(f"State pop: {self.current_state.state_id}")
        else:
            logger.info("State pop: stack is now empty")
        
    def update(self, dt: float, input_snapshot=None):
        """Update the current state."""
        if self.current_state:
            self.current_state.update(dt, input_snapshot)
        
    def render(self, screen: pygame.Surface):
        """Render the current state."""
        if self.current_state:
            self.current_state.render(screen)
        
    def handle_event(self, event: pygame.event.Event) -> None:
        if self.game.ui_manager.has_focus():
            if hasattr(event, "pos"):
                # Mouse event
                if self.game.ui_manager.is_point_inside_panel(event.pos):
                    return None  # Block mouse events inside panel
                else:
                    # Mouse event outside panel: allow
                    if self.current_state:
                        return self.current_state.handle_event(event)
            else:
                # Block all non-mouse events when UI is focused
                return None
        else:
            # No UI focus, always forward to state
            if self.current_state:
                return self.current_state.handle_event(event)

    change_state = set_state  # Alias for compatibility 

    def render_world(self, surface):
        # Render game world
        self.renderer.render_world(surface, self.camera) 