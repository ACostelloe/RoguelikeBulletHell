import pygame
from typing import Dict, List, Optional, Tuple, Any, Set
import random
import json
import os
from zone_template import ZoneTemplateGenerator
from tile_rules import get_tile_variant
from zone_template_loader import ZoneTemplateLoader
from zone_template import ZoneTemplate
from zone_types import Zone, ZoneTransition
from config import ZONE_SIZE, ZONE_LOAD_DISTANCE, BIOME_SETTINGS
import noise
from logger import logger
import traceback
from asset_manager import AssetManager
from tiles import TileFactory
from zone import Zone
from zone_template import ZoneTemplate
from chunk_system import ChunkManager, Camera
from visual_effects import TilesetManager
from components import TransformComponent
from zone_builder import ZoneBuilder
from entities import Entity, EntityType
from components import ZoneComponent

class WorldManagerError(Exception):
    """Base exception for world manager errors."""
    pass

class ZoneGenerationError(WorldManagerError):
    """Raised when zone generation fails."""
    pass

class NoiseGenerationError(WorldManagerError):
    """Raised when noise generation fails."""
    pass

class WorldManager:
    """Manages the game world and its zones."""
    
    def __init__(self, asset_manager: AssetManager, zone_template_loader: ZoneTemplateLoader, chunk_manager: ChunkManager, camera: Camera, entity_manager, bullet_manager, enemy_manager, player, particle_manager):
        """Initialize the world manager."""
        # Initialize seed for noise generation
        self.seed = 42  # Default seed value
        # Initialize random module
        self.random = random.Random(self.seed)

        self.asset_manager = asset_manager
        self.zone_templates = {}
        self.current_zone = None
        self.tile_factory = TileFactory(asset_manager)
        self.template_loader = zone_template_loader
        self.zone_builder = ZoneBuilder(self.tile_factory, entity_manager)
        self.zones: Dict[Tuple[int, int], Entity] = {}
        self.active_zones: Set[Tuple[int, int]] = set()
        self.zone_states: Dict[str, Dict] = {}
        self.initial_load_distance = 1  # Start with just 1 zone in each direction
        self.max_load_distance = 2  # Maximum load distance for scaling
        self.zone_size = ZONE_SIZE
        
        # Initialize pygame and get screen dimensions
        pygame.init()
        screen_info = pygame.display.Info()
        self.screen_width = screen_info.current_w
        self.screen_height = screen_info.current_h
        
        # Initialize chunk system with screen dimensions
        self.chunk_system = chunk_manager
        self.camera = camera
        self.active_zone: Optional[Entity] = None
        
        # Initialize managers
        self.entity_manager = entity_manager
        self.bullet_manager = bullet_manager
        self.enemy_manager = enemy_manager
        self.particle_manager = particle_manager
        self.noise_scale = 0.1  # Perlin noise scaling
        
        # Zone settings
        self.show_debug_overlay = False
        self.debug_font = pygame.font.Font(None, 20)
        
        # Debug tracking
        self.last_accessed_zone = None
        self.zone_access_count = 0
        
        # Biome noise settings
        self.biome_scale = 0.1
        self.biome_threshold = 0.5
        
        # Load zone templates
        self.template_loader.reload_templates()
        
        # Zone state persistence
        self._load_zone_states()
        
        # Initialize starting zone
        self._initialize_starting_zone()
        
        # Generate initial zones
        self._generate_initial_zones()
        
        logger.info("WorldManager initialized successfully")
        
    def initialize(self):
        """Initialize after video mode is set."""
        self.tile_factory.initialize()
        
    def _initialize_starting_zone(self):
        """Initialize the starting zone."""
        # Get a random starting zone template
        start_template = self.template_loader.get_random_template("forest", "start")
        if not start_template:
            raise ZoneGenerationError("No starting zone template found")
        # Create the starting zone using ZoneBuilder
        start_zone = self.zone_builder.build_zone(start_template, x=0, y=0, zone_id="start_zone")
        # Add the zone to the world
        self.zones[(0, 0)] = start_zone
        self.current_zone = start_zone
        self.active_zones.add(start_zone)
        logger.info(f"Initialized starting zone: {start_zone.name}")

    def _load_zone_states(self):
        """Load saved zone states from disk."""
        try:
            if os.path.exists('zone_states.json'):
                with open('zone_states.json', 'r') as f:
                    self.zone_states = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load zone states: {str(e)}")
            logger.error(traceback.format_exc())

    def _save_zone_states(self):
        """Save zone states to disk."""
        try:
            with open('zone_states.json', 'w') as f:
                json.dump(self.zone_states, f)
        except Exception as e:
            logger.error(f"Failed to save zone states: {str(e)}")
            logger.error(traceback.format_exc())

    def _generate_initial_zones(self):
        """Generate the initial set of zones around the player."""
        print("✅ _generate_initial_zones START")
        center_x, center_y = 0, 0
        
        # Start with a smaller initial load distance
        for x in range(-self.initial_load_distance, self.initial_load_distance + 1):
            for y in range(-self.initial_load_distance, self.initial_load_distance + 1):
                print(f"✅ Generating initial zone at ({x}, {y})", flush=True)
                self._generate_zone(x, y)
                print(f"✅ Initial zone at ({x}, {y}) generated", flush=True)

    def _get_biome_type(self, x: int, y: int) -> str:
        print(f"➡️ _get_biome_type entered for zone ({x},{y})", flush=True)
        noise_value = self._get_noise_value(x * self.biome_scale, y * self.biome_scale)
        print(f"🎲 Noise value: {noise_value}", flush=True)
        if noise_value < 0.25:
            print("🌳 Returning biome: forest", flush=True)
            return "forest"
        elif noise_value < 0.5:
            print("🤖 Returning biome: tech", flush=True)
            return "tech"
        elif noise_value < 0.75:
            print("🔥 Returning biome: lava", flush=True)
            return "lava"
        else:
            print("❄️ Returning biome: ice", flush=True)
            return "ice"
    
    def _get_noise_value(self, x: float, y: float, scale: float = 0.1) -> float:
        """Get a noise value for the given coordinates with error handling."""
        try:
            return noise.pnoise2(x * scale, y * scale, base=self.seed % 1024)
        except Exception as e:
            logger.error(f"Noise generation error: {str(e)}")
            logger.error(traceback.format_exc())
            raise NoiseGenerationError(f"Failed to generate noise at ({x}, {y}): {str(e)}")
    
    def _select_zone_template(self, biome: str) -> Optional[ZoneTemplate]:
        """Select a random zone template for the given biome."""
        templates = self.template_loader.get_templates_by_biome(biome)
        if templates:
            return self.random.choice(templates)
        return None
    
    def _get_zone_type(self, x: int, y: int) -> str:
        """Determine the zone type based on coordinates."""
        # For now, use a simple deterministic approach
        # Later this could be based on noise, distance from center, etc.
        if x == 0 and y == 0:
            return "start"
        elif abs(x) <= 1 and abs(y) <= 1:
            return "early_game"
        else:
            return "boss_zone"  # Changed from mid_game to boss_zone since we have templates for that
            
    def _generate_zone(self, x: int, y: int) -> None:
        """Generate a zone with validation and error handling."""
        try:
            zone_id = f"zone_{x}_{y}"
            
            # Skip if zone already exists
            if (x, y) in self.zones:
                logger.debug(f"Zone {zone_id} already exists, skipping generation")
                return
                
            biome = self._get_biome_type(x, y)
            zone_type = self._get_zone_type(x, y)
            logger.info(f"Generating zone at ({x}, {y}), biome: {biome}, zone_type: {zone_type}")
            
            # Get template
            template = self._select_zone_template(biome)
            if not template:
                raise ZoneGenerationError(f"No template found for biome {biome}")
                
            # Validate template
            if not self._validate_zone_template(template):
                raise ZoneGenerationError(f"Invalid template for zone {zone_id}")
                
            # Build zone
            zone = self.zone_builder.build_zone(template, x, y, zone_id)
            
            # Validate zone
            if not self._validate_zone(zone):
                raise ZoneGenerationError(f"Invalid zone {zone_id}")
                
            # Store zone
            self.zones[(x, y)] = zone
            logger.info(f"Successfully generated zone {zone_id}")
            
            # Apply saved state if exists
            if zone_id in self.zone_states:
                self._apply_zone_state(zone, self.zone_states[zone_id])
                logger.info(f"Applied saved state to zone {zone_id}")
                
            # Spawn biome particles
            self._spawn_biome_particles(biome, x, y)
            
        except Exception as e:
            logger.error(f"Error generating zone at ({x}, {y}): {str(e)}")
            logger.error(traceback.format_exc())
            raise ZoneGenerationError(f"Failed to generate zone at ({x}, {y}): {str(e)}")

    def _apply_zone_state(self, zone: Entity, state: Dict[str, Any]) -> None:
        """Apply saved state to a zone."""
        try:
            # Apply entity states
            if 'entities' in state:
                zone.entities = state['entities']
            
            # Apply other zone-specific state
            if 'properties' in state:
                for key, value in state['properties'].items():
                    setattr(zone, key, value)
        except Exception as e:
            logger.error(f"Failed to apply zone state: {str(e)}")
            logger.error(traceback.format_exc())

    def _spawn_biome_particles(self, biome: str, x: int, y: int) -> None:
        """Spawn biome-specific particles with error handling."""
        try:
            if self.particle_manager is None:
                logger.warning("Particle manager not initialized, skipping biome particle spawn")
                return

            # Create a temporary entity for particle emission
            temp_entity = self.entity_manager.create_entity(EntityType.EFFECT)
            
            # Add zone component
            zone_component = ZoneComponent(temp_entity)
            zone_component.zone_type = biome
            zone_component.position = (x * ZONE_SIZE, y * ZONE_SIZE)
            temp_entity.add_component(zone_component)
            
            # Add to zones
            self.zones[(x, y)] = temp_entity
            
            if biome == "forest":
                self.particle_manager.emit_particles(temp_entity, "leaves", count=5)
            elif biome == "tech":
                self.particle_manager.emit_particles(temp_entity, "sparks", count=5)
            elif biome == "lava":
                self.particle_manager.emit_particles(temp_entity, "embers", count=5)
            elif biome == "ice":
                self.particle_manager.emit_particles(temp_entity, "frost", count=5)
        except Exception as e:
            logger.error(f"Failed to spawn biome particles: {str(e)}")
            logger.error(traceback.format_exc())

    def update(self, camera_x: float, camera_y: float):
        """Update the world state and load/unload zones as needed."""
        try:
            # Convert camera position to zone coordinates
            zone_x = int(camera_x // (self.zone_size * 32))  # 32 is tile size
            zone_y = int(camera_y // (self.zone_size * 32))
            
            # Check if we need to load more zones
            current_distance = max(abs(zone_x), abs(zone_y))
            
            # Track which zones should be active
            new_active_zones = set()
            
            # Determine which zones should be active based on distance
            for x in range(zone_x - self.max_load_distance, zone_x + self.max_load_distance + 1):
                for y in range(zone_y - self.max_load_distance, zone_y + self.max_load_distance + 1):
                    new_active_zones.add((x, y))
                    
                    # Only generate zone if it doesn't exist
                    if (x, y) not in self.zones:
                        logger.info(f"Loading new zone at ({x}, {y})")
                        self._generate_zone(x, y)
                        logger.info(f"New zone at ({x}, {y}) loaded")
            
            # Update active zones
            self.active_zones = new_active_zones
            
            # Unload zones that are too far away
            zones_to_unload = set(self.zones.keys()) - new_active_zones
            for zone_coords in zones_to_unload:
                if zone_coords in self.zones:
                    logger.info(f"Unloading zone at {zone_coords}")
                    del self.zones[zone_coords]
            
        except Exception as e:
            logger.error(f"Error updating world: {str(e)}")
            logger.error(traceback.format_exc())

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        """Draw the world and its contents."""
        # Draw active zones
        for zone in self.active_zones:
            self._draw_zone(screen, zone, zone.x, zone.y, camera_x, camera_y)
            
        # Draw debug overlay if enabled
        if self.show_debug_overlay:
            self._draw_debug_overlay(screen, camera_x, camera_y)

    def render(self, screen: pygame.Surface, camera) -> None:
        """Render the world and its contents using the provided camera."""
        if hasattr(camera, 'get_component'):
            # Handle Entity camera with TransformComponent
            camera_transform = camera.get_component(TransformComponent)
            camera_x = camera_transform.x if camera_transform else 0
            camera_y = camera_transform.y if camera_transform else 0
        else:
            # Handle Camera object from chunk_system.py
            camera_x = camera.x if camera else 0
            camera_y = camera.y if camera else 0
            
        # Calculate view frustum
        view_width = screen.get_width()
        view_height = screen.get_height()
        view_frustum = pygame.Rect(
            camera_x - view_width/2,
            camera_y - view_height/2,
            view_width,
            view_height
        )

        # Render active zones
        for zone in self.active_zones:
            # Check if zone is in view
            zone_rect = pygame.Rect(zone.x, zone.y, self.zone_size * 32, self.zone_size * 32)
            if not zone_rect.colliderect(view_frustum):
                continue
            self._draw_zone(screen, zone, zone.x, zone.y, camera_x, camera_y)

        # Draw debug overlay if enabled
        if self.show_debug_overlay:
            self._draw_debug_overlay(screen, camera_x, camera_y)

    def get_spawn_position(self) -> Tuple[int, int]:
        """Get a valid spawn position in the starting zone."""
        start_zone = self.current_zone
        
        # Find a suitable platform in the starting zone
        for tile in start_zone.tiles:
            if tile.type in ["platform_left", "platform_middle", "platform_right"]:
                return (tile.x + 16, tile.y - 40)  # Center of platform, above it
        
        # Fallback spawn position
        return (self.screen_width // 2, self.screen_height // 2)
    
    def get_enemy_spawns(self, player_x: float, player_y: float) -> List[Dict]:
        """Get enemy spawns from active zones near the player."""
        spawns = []
        for zone in self.active_zones:
            for enemy in zone.template.enemies:
                # Convert enemy position to world coordinates
                enemy_world_x = enemy.x * ZONE_SIZE
                enemy_world_y = enemy.y * ZONE_SIZE
                
                # Only include enemies within spawn distance
                if (abs(enemy_world_x - player_x) <= ZONE_SIZE * 2 and 
                    abs(enemy_world_y - player_y) <= ZONE_SIZE * 2):
                    spawns.append({
                        'type': enemy.type,
                        'x': enemy_world_x,
                        'y': enemy_world_y,
                        'patrol_points': enemy.patrol_points,
                        'biome': zone.template.biome
                    })
        return spawns
    
    def get_loot_spawns(self, player_x: float, player_y: float, radius: int = 3) -> List[Dict]:
        """Get loot spawns from active zones near the player."""
        spawns = []
        for zone in self.active_zones:
            for loot in zone.template.loot:
                loot_world_x = loot.x * ZONE_SIZE
                loot_world_y = loot.y * ZONE_SIZE
                if (abs(loot_world_x - player_x) <= radius * ZONE_SIZE and
                    abs(loot_world_y - player_y) <= radius * ZONE_SIZE):
                    spawns.append({
                        'type': loot.type,
                        'x': loot_world_x,
                        'y': loot_world_y,
                        'rarity': loot.rarity
                    })
        return spawns

    def get_zone_at(self, x: int, y: int) -> Optional[Entity]:
        """Get the zone at the specified world coordinates."""
        try:
            # Convert world coordinates to zone coordinates
            zone_x = int(x // (self.zone_size * 32))  # 32 is tile size
            zone_y = int(y // (self.zone_size * 32))
            
            # Get zone from the zones dictionary
            zone = self.zones.get((zone_x, zone_y))
            
            # Debug tracking
            if zone:
                self.last_accessed_zone = zone.id
                self.zone_access_count += 1
                if self.zone_access_count % 100 == 0:  # Log every 100 accesses
                    print(f"🔍 Zone access count: {self.zone_access_count}, Last accessed: {self.last_accessed_zone}")
            
            return zone
            
        except Exception as e:
            logger.error(f"Error getting zone at ({x}, {y}): {str(e)}")
            logger.error(traceback.format_exc())
            return None

    def _draw_zone(self, screen: pygame.Surface, zone: Entity, 
                  zone_x: int, zone_y: int, camera_x: float, camera_y: float):
        """Draw a single zone."""
        # Calculate zone position relative to camera
        world_x = zone_x * ZONE_SIZE
        world_y = zone_y * ZONE_SIZE
        screen_x = world_x - camera_x
        screen_y = world_y - camera_y
        
        # Draw tiles
        for tile in zone.tiles:
            tile_screen_x = screen_x + tile.x * ZONE_SIZE
            tile_screen_y = screen_y + tile.y * ZONE_SIZE
            
            # Only draw if on screen
            if (0 <= tile_screen_x < self.screen_width and 
                0 <= tile_screen_y < self.screen_height):
                tile_image = None  # TODO: Replace with new tile system
                if tile_image:
                    screen.blit(tile_image, (tile_screen_x, tile_screen_y))
        
        # Draw decorations
        for decoration in zone.decorations:
            dec_screen_x = screen_x + decoration.x * ZONE_SIZE
            dec_screen_y = screen_y + decoration.y * ZONE_SIZE
            
            if (0 <= dec_screen_x < self.screen_width and 
                0 <= dec_screen_y < self.screen_height):
                # TODO: Replace with new decoration system
                pass

    def get_transition_at(self, player_x: int, player_y: int) -> Optional[ZoneTransition]:
        """Return the transition at the player's position, if any."""
        zone = self.get_zone_at(player_x, player_y)
        if not zone or not hasattr(zone.template, 'transitions'):
            return None
        # Convert player position to tile coordinates within the zone
        zone_x = int((player_x % ZONE_SIZE) / (ZONE_SIZE // zone.template.width))
        zone_y = int((player_y % ZONE_SIZE) / (ZONE_SIZE // zone.template.height))
        for transition in getattr(zone.template, 'transitions', []):
            if transition.x == zone_x and transition.y == zone_y:
                return transition
        return None

    def handle_player_transition(self, player) -> bool:
        """Check if the player is on a transition tile and handle the transition."""
        try:
            transition = self.get_transition_at(player.rect.centerx, player.rect.centery)
            if transition:
                logger.info(f"Player transition detected: {transition.target}")
                # Example: teleport player to target zone (expand as needed)
                if transition.target:
                    # Find the target zone and set player position to its spawn
                    for zone in self.active_zones:
                        if zone.template.name == transition.target:
                            spawn_positions = zone.template.get_spawn_positions()
                            if spawn_positions:
                                spawn_x, spawn_y = spawn_positions[0]
                                player.rect.x = zone.x + spawn_x * (ZONE_SIZE // zone.template.width)
                                player.rect.y = zone.y + spawn_y * (ZONE_SIZE // zone.template.height)
                                logger.info(f"Player transitioned to zone {transition.target}")
                                return True
            return False
        except Exception as e:
            logger.error(f"Error handling player transition: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    def get_platforms(self) -> List[pygame.Rect]:
        """Get all platforms from active zones."""
        platforms = []
        for zone in self.active_zones:
            for tile in zone.tiles:
                if tile.is_platform:
                    platforms.append(tile.rect)
        return platforms 

    def handle_input(self, keys):
        """Handle input events."""
        if keys[pygame.K_d]:
            self.show_debug_overlay = not self.show_debug_overlay
            print(f"Debug overlay {'enabled' if self.show_debug_overlay else 'disabled'}")
                
    def _draw_debug_overlay(self, screen, camera_x, camera_y):
        """Draw debug information about zones."""
        if not self.show_debug_overlay:
            return
            
        # Draw zone boundaries
        for zone in self.active_zones:
            # Calculate screen position
            screen_x = zone.x / ZONE_SIZE - camera_x + screen.get_width() // 2
            screen_y = zone.y / ZONE_SIZE - camera_y + screen.get_height() // 2
            
            # Draw zone boundary
            pygame.draw.rect(screen, (255, 255, 255), 
                           (screen_x, screen_y, self.zone_size, self.zone_size), 1)
            
            # Draw zone info
            text = f"{zone.template.biome}/{zone.template.zone_type}"
            text_surface = self.debug_font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(screen_x + self.zone_size // 2,
                                                     screen_y + self.zone_size // 2))
            screen.blit(text_surface, text_rect)
            
            # Draw entity count
            entity_count = len(zone.entities)
            count_text = f"Entities: {entity_count}"
            count_surface = self.debug_font.render(count_text, True, (255, 255, 255))
            screen.blit(count_surface, (screen_x + 5, screen_y + 25))
            
            # Draw transition tiles
            for transition in zone.template.transitions:
                trans_x = transition.x * 32 - camera_x + screen.get_width() // 2
                trans_y = transition.y * 32 - camera_y + screen.get_height() // 2
                pygame.draw.rect(screen, (255, 255, 0), 
                               (trans_x, trans_y, 32, 32), 2)
                trans_text = f"->{transition.target}"
                trans_surface = self.debug_font.render(trans_text, True, (255, 255, 0))
                screen.blit(trans_surface, (trans_x, trans_y - 20))
                
            # Draw last accessed indicator
            if zone.id == self.last_accessed_zone:
                pygame.draw.rect(screen, (0, 255, 0),
                               (screen_x, screen_y, self.zone_size, self.zone_size), 3)

    def _validate_zone(self, zone: Entity) -> bool:
        """Validate a zone's state and structure."""
        try:
            # Check required attributes
            if not hasattr(zone, 'id') or not zone.id:
                print(f"[Zone Validation] Missing or invalid zone ID at {zone.position if hasattr(zone, 'position') else 'unknown position'}")
                return False
            if not hasattr(zone, 'template') or not zone.template:
                print(f"[Zone Validation] Missing or invalid template for zone {zone.id}")
                return False
            if not hasattr(zone, 'x') or not hasattr(zone, 'y'):
                print(f"[Zone Validation] Missing position coordinates for zone {zone.id}")
                return False
            
            # Validate template
            if not self._validate_zone_template(zone.template):
                print(f"[Zone Validation] Template validation failed for zone {zone.id}")
                return False
            
            # Validate tiles
            if not hasattr(zone.template, 'tiles') or not isinstance(zone.template.tiles, list):
                print(f"[Zone Validation] Missing or invalid tiles list in zone {zone.id}")
                return False
            if not zone.template.tiles:
                print(f"[Zone Validation] Empty tiles list in zone {zone.id}")
                return False
            
            # Validate dimensions
            if not hasattr(zone.template, 'width') or not hasattr(zone.template, 'height'):
                print(f"[Zone Validation] Missing dimensions in zone {zone.id}")
                return False
            if zone.template.width <= 0 or zone.template.height <= 0:
                print(f"[Zone Validation] Invalid dimensions ({zone.template.width}x{zone.template.height}) in zone {zone.id}")
                return False
            
            # Validate entities
            if not self._validate_zone_entities(zone):
                print(f"[Zone Validation] Entity validation failed for zone {zone.id}")
                return False
            
            print(f"[Zone Validation] Zone {zone.id} passed all validation checks")
            return True
        except Exception as e:
            logger.error(f"Zone validation error: {str(e)}")
            logger.error(traceback.format_exc())
            print(f"[Zone Validation] Exception during validation: {str(e)}")
            return False

    def _validate_zone_template(self, template: ZoneTemplate) -> bool:
        """Validate a zone template."""
        try:
            # Check required template attributes
            if not hasattr(template, 'biome') or not template.biome:
                print(f"[Template Validation] Missing or invalid biome in template {template.name if hasattr(template, 'name') else 'unknown'}")
                return False
            if not hasattr(template, 'zone_type') or not template.zone_type:
                print(f"[Template Validation] Missing or invalid zone_type in template {template.name if hasattr(template, 'name') else 'unknown'}")
                return False
            if not hasattr(template, 'width') or not hasattr(template, 'height'):
                print(f"[Template Validation] Missing dimensions in template {template.name if hasattr(template, 'name') else 'unknown'}")
                return False
            
            # Validate biome
            if template.biome not in BIOME_SETTINGS:
                print(f"[Template Validation] Unknown biome '{template.biome}' in template {template.name if hasattr(template, 'name') else 'unknown'}")
                return False
            
            # Validate dimensions
            if template.width <= 0 or template.height <= 0:
                print(f"[Template Validation] Invalid dimensions ({template.width}x{template.height}) in template {template.name if hasattr(template, 'name') else 'unknown'}")
                return False
            
            # Validate tiles
            if not hasattr(template, 'tiles') or not isinstance(template.tiles, list):
                print(f"[Template Validation] Missing or invalid tiles list in template {template.name if hasattr(template, 'name') else 'unknown'}")
                return False
            
            # Validate tile positions
            for tile in template.tiles:
                if not hasattr(tile, 'x') or not hasattr(tile, 'y'):
                    print(f"[Template Validation] Tile missing position coordinates in template {template.name if hasattr(template, 'name') else 'unknown'}")
                    return False
                if not (0 <= tile.x < template.width and 0 <= tile.y < template.height):
                    print(f"[Template Validation] Tile at ({tile.x}, {tile.y}) out of bounds in template {template.name if hasattr(template, 'name') else 'unknown'}")
                    return False
            
            print(f"[Template Validation] Template {template.name if hasattr(template, 'name') else 'unknown'} passed all validation checks")
            return True
        except Exception as e:
            logger.error(f"Template validation error: {str(e)}")
            logger.error(traceback.format_exc())
            print(f"[Template Validation] Exception during validation: {str(e)}")
            return False

    def _validate_zone_entities(self, zone: Entity) -> bool:
        """Validate entities in a zone."""
        try:
            # Check entity IDs
            if not isinstance(zone.entities, list):
                return False
            
            # Check for duplicate entity IDs
            if len(zone.entities) != len(set(zone.entities)):
                return False
            
            return True
        except Exception as e:
            logger.error(f"Entity validation error: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    def cleanup(self):
        """Clean up world manager resources."""
        try:
            # Save zone states
            self._save_zone_states()
            
            # Clear active zones
            self.active_zones.clear()
            
        except Exception as e:
            logger.error(f"World manager cleanup failed: {str(e)}")
            logger.error(traceback.format_exc())

    def load_zone_from_template(self, template: ZoneTemplate) -> Entity:
        zone = Entity(template)
        self.active_zone = zone
        # Optional: Hook for future tile/entity spawning logic
        return zone 

    def create_zone(self, zone_type: str, position: Tuple[float, float]) -> Entity:
        """Create a new zone of the specified type."""
        try:
            # Create zone entity
            zone_entity = self.entity_manager.create_entity(EntityType.EFFECT)
            
            # Add zone component
            zone_component = ZoneComponent(zone_entity)
            zone_component.zone_type = zone_type
            zone_component.position = position
            zone_entity.add_component(zone_component)
            
            # Add to zones
            self.zones[zone_entity.id] = zone_entity
            return zone_entity
            
        except Exception as e:
            logger.error(f"Error creating zone: {str(e)}")
            logger.error(traceback.format_exc())
            return None 

    def generate_zone(self, biome_name):
        """Stub: Generate zone by biome."""
        return Zone(biome=biome_name)

    def set_current_zone(self, zone):
        self.current_zone = zone

# Minimal stub Zone class for test compatibility
class Zone:
    def __init__(self, biome):
        self.biome = biome 