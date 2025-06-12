"""
Main game module.
"""
import traceback
import json
import logging
from datetime import datetime
import os

try:
    from typing import Dict, List, Tuple, Optional, Any, Set
    import pygame
    import sys
    from entities import Entity, Component, TransformComponent, EntityType
    from components import StateComponent, HealthComponent, SpriteComponent
    from player import Player, PlayerStats
    from enemies import Enemy
    from bullets import Bullet, BulletManager
    from powerup import PowerUp
    from particle_system import ParticleSystem
    from audio_manager import AudioManager
    from ui_manager import UIManager, UIComponent
    from game_state import GameStateManager, MenuState, PlayingState, PausedState, PreStartState
    from config import ConfigManager, GameState
    from logger import logger
    from asset_manager import AssetManager
    from renderer import Renderer
    from world_manager import WorldManager
    from entity_manager import EntityManager
    from enemy_manager import EnemyManager
    from chunk_system import ChunkManager
    from zone_template_loader import ZoneTemplateLoader
    from physics_system import PhysicsSystem
    from systems.collision_system import CollisionSystem
    from input_handler import InputManager
    from systems.bullet_system import BulletSystem
    from systems.zone_entity_spawner import ZoneEntitySpawner
    from systems.enemy_system import EnemySystem
    from camera import Camera
except Exception as e:
    print("⚠️ An error occurred during startup:")
    traceback.print_exc()
    sys.exit(1)

# Configure logging
def setup_logging():
    """Configure logging for the game."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"game_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("Game")

class InputSnapshot:
    """Snapshot of input state for a single frame."""
    def __init__(self):
        self.keys = pygame.key.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_buttons = pygame.mouse.get_pressed()

class Game:
    """Main game class."""
    
    def __init__(self):
        """Initialize the game."""
        self.logger = setup_logging()
        self.logger.info("Starting game initialization...")
        
        try:
            pygame.init()
            self.logger.info("Pygame initialized successfully")
            
            self.screen_width = 800
            self.screen_height = 600
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption("Bullet Hell Game")
            self.logger.info(f"Display initialized: {self.screen_width}x{self.screen_height}")
            
            self.clock = pygame.time.Clock()
            self.running = True
            self.fps = 60
            
            # Initialize managers with error handling
            try:
                self.logger.info("Initializing ConfigManager...")
                self.config_manager = ConfigManager()
                if not self.config_manager:
                    raise RuntimeError("ConfigManager initialization failed")
                self.logger.info("ConfigManager initialized successfully")
                
                self.logger.info("Initializing AssetManager...")
                self.asset_manager = AssetManager(asset_dir='assets')
                if not self.asset_manager:
                    raise RuntimeError("AssetManager initialization failed")
                self.logger.info("AssetManager initialized successfully")
                
                self.logger.info("Initializing EntityManager...")
                self.entity_manager = EntityManager()
                if not self.entity_manager:
                    raise RuntimeError("EntityManager initialization failed")
                self.logger.info("EntityManager initialized successfully")
                
                # Initialize UIManager
                self.logger.info("Initializing UIManager...")
                from ui_manager import UIManager
                self.ui_manager = UIManager(self.entity_manager)
                self.logger.info("UIManager initialized successfully")
                
                self.logger.info("Initializing GameStateManager...")
                self.state_manager = GameStateManager(self)
                if not self.state_manager:
                    raise RuntimeError("GameStateManager initialization failed")
                self.logger.info("GameStateManager initialized successfully")
                
                self.logger.info("Initializing Renderer...")
                self.renderer = Renderer(self.screen, self.asset_manager, self.entity_manager)
                if not self.renderer:
                    raise RuntimeError("Renderer initialization failed")
                self.logger.info("Renderer initialized successfully")
                
                self.logger.info("Initializing Camera...")
                self.camera = Camera(self.screen_width, self.screen_height)
                if not self.camera:
                    raise RuntimeError("Camera initialization failed")
                self.logger.info("Camera initialized successfully")
                
                self.logger.info("Initializing EnemyManager...")
                self.enemy_manager = EnemyManager(self.entity_manager)
                if not self.enemy_manager:
                    raise RuntimeError("EnemyManager initialization failed")
                self.logger.info("EnemyManager initialized successfully")
                
                # Initialize PhysicsSystem
                self.physics_system = PhysicsSystem()
                self.logger.info("PhysicsSystem initialized successfully")
                
                # Initialize CollisionSystem
                self.collision = CollisionSystem()
                self.logger.info("CollisionSystem initialized successfully")
                
                # Initialize BulletSystem
                self.bullet_system = BulletSystem(self.entity_manager)
                self.logger.info("BulletSystem initialized successfully")
                
                # Initialize EnemySystem
                self.enemy_system = EnemySystem(self.entity_manager)
                self.logger.info("EnemySystem initialized successfully")
                
                # Initialize ZoneEntitySpawner
                self.zone_entity_spawner = ZoneEntitySpawner(self.entity_manager)
                self.logger.info("ZoneEntitySpawner initialized successfully")
                
                # Initialize ChunkManager
                self.logger.info("Initializing ChunkManager...")
                self.chunk_manager = ChunkManager(self.screen_width, self.screen_height)
                if not self.chunk_manager:
                    raise RuntimeError("ChunkManager initialization failed")
                self.logger.info("ChunkManager initialized successfully")
                
                # Initialize BulletManager
                self.logger.info("Initializing BulletManager...")
                self.bullet_manager = BulletManager(self.entity_manager)
                if not self.bullet_manager:
                    raise RuntimeError("BulletManager initialization failed")
                self.logger.info("BulletManager initialized successfully")
                
                # Initialize Player
                self.logger.info("Initializing Player...")
                self.player = Player(100, 100)
                if not self.player:
                    raise RuntimeError("Player initialization failed")
                self.logger.info("Player initialized successfully")
                
                # Initialize ParticleManager
                self.logger.info("Initializing ParticleManager...")
                self.particle_manager = ParticleSystem()
                if not self.particle_manager:
                    raise RuntimeError("ParticleManager initialization failed")
                self.logger.info("ParticleManager initialized successfully")
                
                # Initialize ZoneTemplateLoader before WorldManager
                self.logger.info("Initializing ZoneTemplateLoader...")
                self.zone_template_loader = ZoneTemplateLoader(self.entity_manager, "configs/zones")
                if not self.zone_template_loader:
                    raise RuntimeError("ZoneTemplateLoader initialization failed")
                self.logger.info("ZoneTemplateLoader initialized successfully")
                
                # Initialize WorldManager with all required dependencies
                self.logger.info("Initializing WorldManager...")
                self.world_manager = WorldManager(
                    self.asset_manager,
                    self.zone_template_loader,
                    self.chunk_manager,
                    self.camera,
                    self.entity_manager,
                    self.bullet_manager,
                    self.enemy_manager,
                    self.player,
                    self.particle_manager
                )
                self.logger.info("WorldManager initialized successfully")
                
            except Exception as e:
                self.logger.error(f"Error during manager initialization: {str(e)}")
                self.logger.error(traceback.format_exc())
                raise
            
            # Load assets with error handling
            try:
                self.logger.info("Loading game assets...")
                self.asset_manager.load_all()
                self.logger.info("Main assets loaded successfully")
                
                self.logger.info("Loading background tiles...")
                self.asset_manager.load_background()
                self.logger.info("Background tiles loaded successfully")
            except Exception as e:
                self.logger.error(f"Error during asset loading: {str(e)}")
                self.logger.error(traceback.format_exc())
                raise
            
            # Initialize game state
            try:
                self.logger.info("Setting up game state...")
                self.setup_game()
                self.logger.info("Game state setup completed successfully")
            except Exception as e:
                self.logger.error(f"Error during game state setup: {str(e)}")
                self.logger.error(traceback.format_exc())
                raise
                
        except Exception as e:
            self.logger.critical(f"Critical error during game initialization: {str(e)}")
            self.logger.critical(traceback.format_exc())
            raise
        
    def _set_display(self, screen_width, screen_height):
        print(f"[PYGAME VIDEO DRIVER]: {pygame.display.get_driver()}")
        print(f"[DISPLAY INIT] Attempting to set display: {screen_width}x{screen_height}")
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        
    def create_ui(self):
        """Create UI elements."""
        try:
            # Create main menu panel
            menu = self.ui_manager.create_element('menu', 'panel', (0, 0), (800, 600), style={
                'background_color': (20, 20, 40),
                'border_color': (100, 100, 150),
                'border_width': 2
            })
            if menu:
                # Title text
                menu_title = self.ui_manager.create_element('menu_title', 'text', (0, 100), (800, 80),
                    parent='menu',
                    style={
                        'font_color': (255, 255, 255),
                        'font': pygame.font.Font(None, 74),
                        'background_color': (0, 0, 0, 0)
                    }
                )
                menu_title_component = menu_title.get_component(UIComponent)
                menu_title_component.data['text'] = 'Bullet Hell Game'
                menu_title_component.visible = True
                menu_title_component.enabled = True

                # Instructions text
                menu_instructions = self.ui_manager.create_element('menu_instructions', 'text', (0, 250), (800, 50),
                    parent='menu',
                    style={
                        'font_color': (200, 200, 200),
                        'font': pygame.font.Font(None, 36),
                        'background_color': (0, 0, 0, 0)
                    }
                )
                menu_instructions_component = menu_instructions.get_component(UIComponent)
                menu_instructions_component.data['text'] = 'Press ENTER to Start'
                menu_instructions_component.visible = True
                menu_instructions_component.enabled = True
                
                # Set menu as focused element
                self.ui_manager.focused_element = "menu_instructions"
            
            # Create HUD
            hud = self.ui_manager.create_element("hud", "panel", (0, 0), (800, 600), style={
                'background_color': (0, 0, 0, 0)  # Transparent background
            })
            if hud:
                # Health bar
                health_bar = self.ui_manager.create_element(
                    "health_bar", "progress_bar",
                    (20, 20), (200, 20),
                    parent="hud",
                    style={
                        "background_color": (50, 50, 50),
                        "foreground_color": (200, 50, 50),
                        "border_color": (100, 100, 100),
                        "border_width": 2
                    }
                )
                health_bar.get_component(UIComponent).visible = True
                health_bar.get_component(UIComponent).enabled = True
                
                # Experience bar
                exp_bar = self.ui_manager.create_element(
                    "exp_bar", "progress_bar",
                    (20, 50), (200, 10),
                    parent="hud",
                    style={
                        "background_color": (50, 50, 50),
                        "foreground_color": (50, 200, 50),
                        "border_color": (100, 100, 100),
                        "border_width": 1
                    }
                )
                exp_bar.get_component(UIComponent).visible = True
                exp_bar.get_component(UIComponent).enabled = True
                
                default_font = pygame.font.Font(None, 24)
                
                # Score display
                score = self.ui_manager.create_element(
                    "score", "text",
                    (20, 70), (200, 30),
                    parent="hud",
                    style={
                        "font": default_font,
                        "font_color": (255, 255, 255),
                        "background_color": (0, 0, 0, 0)  # Transparent background
                    }
                )
                score.get_component(UIComponent).visible = True
                score.get_component(UIComponent).enabled = True
                
                # Level display
                level = self.ui_manager.create_element(
                    "level", "text",
                    (20, 110), (200, 30),
                    parent="hud",
                    style={
                        "font": default_font,
                        "font_color": (255, 255, 255),
                        "background_color": (0, 0, 0, 0)  # Transparent background
                    }
                )
                level.get_component(UIComponent).visible = True
                level.get_component(UIComponent).enabled = True
                
            # Create pause menu panel
            pause = self.ui_manager.create_element('pause', 'panel', (200, 200), (400, 200), style={
                'background_color': (40, 40, 60),
                'border_color': (100, 100, 150),
                'border_width': 2
            })
            if pause:
                pause_text = self.ui_manager.create_element('pause_text', 'text', (250, 250), (300, 50), 
                    parent='pause', 
                    style={ 
                        'font_color': (255, 255, 0), 
                        'font': pygame.font.Font(None, 36),
                        'background_color': (0, 0, 0, 0)
                    }
                )
                pause_text.get_component(UIComponent).data['text'] = 'PAUSED'
                pause_text.get_component(UIComponent).visible = True
                pause_text.get_component(UIComponent).enabled = True

            # Create debug overlay
            debug = self.ui_manager.create_element('debug_overlay', 'panel', (10, 10), (200, 30), style={
                'background_color': (255, 0, 0, 128),  # Semi-transparent red
                'border_color': (255, 255, 255),
                'border_width': 1
            })
            if debug:
                debug_text = self.ui_manager.create_element('debug_text', 'text', (20, 15), (180, 20),
                    parent='debug_overlay',
                    style={
                        'text_color': (255, 255, 255),
                        'font': pygame.font.Font(None, 24),
                        'background_color': (0, 0, 0, 0)  # Transparent background
                    }
                )
                debug_text.get_component(UIComponent).text = 'UI Debug Active'
                debug_text.get_component(UIComponent).visible = True
                debug_text.get_component(UIComponent).enabled = True
                debug.get_component(UIComponent).layer = 100  # Ensure it's on top
            
            # Add Continue button for prestart state
            prestart_panel = self.ui_manager.create_element('prestart', 'panel', (0, 0), (800, 600), style={
                'background_color': (30, 30, 50),
                'border_color': (100, 100, 150),
                'border_width': 2
            })
            if prestart_panel:
                continue_button = self.ui_manager.create_element('prestart_continue', 'button', (300, 400), (200, 60),
                    parent='prestart',
                    style={
                        'font_color': (255, 255, 255),
                        'font': pygame.font.Font(None, 48),
                        'background_color': (60, 120, 60),
                        'border_color': (100, 255, 100),
                        'border_width': 3
                    }
                )
                continue_button_component = continue_button.get_component(UIComponent)
                continue_button_component.data['text'] = 'Continue'
                continue_button_component.visible = True
                continue_button_component.enabled = True
            
        except Exception as e:
            logger.error(f"Error creating UI: {str(e)}")
            logger.error(traceback.format_exc())
            
    def handle_event(self, event):
        """Handle a single event."""
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
        self.state_manager.handle_event(event)

    def game_loop(self):
        """Main game loop."""
        while self.running:
            delta_time = self.clock.tick(self.fps) / 1000.0
            
            self.handle_events()
            self.update(delta_time)
            self.renderer.render_all(
                self.screen,
                self.camera,
                self.world_manager,
                self.entity_manager,
                self.bullet_manager,
                self.enemy_manager,
                self.ui_manager
            )
            pygame.display.flip()

    def run(self):
        """Run the game."""
        try:
            self.game_loop()
        except Exception as e:
            logger.error(f"Error in game loop: {str(e)}")
            logger.error(traceback.format_exc())
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources."""
        try:
            # Save configuration
            self.config_manager.save_config("config.json")
            
            # Quit pygame
            pygame.quit()
            
        except Exception as e:
            logger.error(f"Error cleaning up: {str(e)}")
            logger.error(traceback.format_exc())

    def handle_gameplay_event(self, event):
        # Logic for handling events only during gameplay
        self.ui_manager.handle_event(event)
        # Handle more events here if needed

    def _generate_initial_level(self):
        """Generate initial level with test enemies."""
        # Create player
        player = Entity(EntityType.PLAYER)
        transform = TransformComponent(player)
        transform.x = 400
        transform.y = 300
        player.add_component(transform)
        
        sprite = SpriteComponent(player)
        sprite.image = self.asset_manager.get_image("player")
        player.add_component(sprite)
        
        self.entity_manager.add_entity(player)
        
        # Create test enemies
        enemy_types = ["grunt", "flyer", "tank", "boss"]
        positions = [(100, 100), (200, 200), (300, 300), (400, 400)]
        
        for enemy_type, (x, y) in zip(enemy_types, positions):
            enemy = Entity(EntityType.ENEMY)
            transform = TransformComponent(enemy)
            transform.x = x
            transform.y = y
            enemy.add_component(transform)
            
            sprite = SpriteComponent(enemy)
            sprite.image = self.asset_manager.get_image(f"enemies/{enemy_type}")
            enemy.add_component(sprite)
            
            self.entity_manager.add_entity(enemy)
            
        self.logger.info("Initial level generated with test entities")

    def create_states(self):
        """Create game states."""
        try:
            self.logger.info("Creating game states...")
            
            # Create menu state
            self.logger.info("Creating menu state...")
            menu_state = MenuState(self)
            if not menu_state:
                raise RuntimeError("Failed to create MenuState")
            self.logger.info("Menu state created successfully")
            
            # Create playing state
            self.logger.info("Creating playing state...")
            playing_state = PlayingState(self)
            if not playing_state:
                raise RuntimeError("Failed to create PlayingState")
            self.logger.info("Playing state created successfully")
            
            # Create paused state
            self.logger.info("Creating paused state...")
            paused_state = PausedState(self)
            if not paused_state:
                raise RuntimeError("Failed to create PausedState")
            self.logger.info("Paused state created successfully")
            
            # Create pre-start state
            self.logger.info("Creating pre-start state...")
            pre_start_state = PreStartState(self)
            if not pre_start_state:
                raise RuntimeError("Failed to create PreStartState")
            self.logger.info("Pre-start state created successfully")
            
            # Register states with state manager
            self.logger.info("Registering states with state manager...")
            self.state_manager.add_state("menu", menu_state)
            self.state_manager.add_state("playing", playing_state)
            self.state_manager.add_state("paused", paused_state)
            self.state_manager.add_state("pre_start", pre_start_state)
            self.logger.info("States registered successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating game states: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            # Check if UI has focus first
            if self.ui_manager.has_focus():
                self.ui_manager.handle_event(event)
                continue

            if event.type == pygame.QUIT:
                self.running = False
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
                return
                
            # If UI didn't handle it, pass to game state
            self.state_manager.handle_event(event)

    def update(self, delta_time: float):
        """Update game state."""
        # Run entity audits
        self.entity_manager.run_audits()
        
        # Update systems
        self.physics_system.update(delta_time)
        self.collision.update(delta_time)
        self.bullet_system.update(delta_time)
        self.enemy_system.update(delta_time)
        self.zone_entity_spawner.update(delta_time)
        self.world_manager.update(delta_time, self.camera.y)
        self.particle_manager.update(delta_time)
        self.ui_manager.update(delta_time)
        
    def load_config(self):
        """Load game configuration."""
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            logger.warning("No config file found. Using defaults.")
            self.config = {
                "screen_width": 800,
                "screen_height": 600,
                "fps": 60
            }

    def load_assets(self):
        """Load game assets."""
        try:
            self.asset_manager.load_all()
        except Exception as e:
            logger.error(f"Error loading assets: {str(e)}")
            logger.error(traceback.format_exc())

    def setup_ui(self):
        """Set up the game's UI."""
        self.create_ui()

    def setup_game(self):
        """Set up initial game state."""
        try:
            self.logger.info("Setting up initial game state...")
            
            # Create UI
            self.logger.info("Creating UI elements...")
            self.create_ui()
            self.logger.info("UI elements created successfully")
            
            # Create game states
            self.logger.info("Creating game states...")
            self.create_states()
            self.logger.info("Game states created successfully")
            
            # Generate initial level
            self.logger.info("Generating initial level...")
            self._generate_initial_level()
            self.logger.info("Initial level generated successfully")
            
            # Verify state manager
            if not self.state_manager:
                raise RuntimeError("GameStateManager is not initialized")
            
            # Transition to initial state
            self.logger.info("Transitioning to initial state...")
            self.state_manager.change_state("pre_start")
            self.logger.info("Successfully transitioned to initial state")
            
            self.logger.info("Game setup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during game setup: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

if __name__ == "__main__":
    game = Game()
    game.run()
    game.cleanup() 