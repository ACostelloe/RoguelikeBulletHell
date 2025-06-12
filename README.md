# FINAL ECS STABILIZATION PATCH: ECS rendering pipeline now fully stable.

# SPRITECOMPONENT UNIFICATION PATCH: All imports stabilized, duplicate class removed

# ASSET BRIDGE PATCH COMPLETE: SpriteComponent keys fully aligned with loaded assets

# ENTITY REGISTRATION PATCH: Entities now properly added to ECS world

# ECS RENDERING EXPANSION PATCH COMPLETE: Full entity rendering and camera integration

# SPRITE COMPONENT BRIDGE PATCH: ECS entities now visible in renderer

# EnemyManager created: ECS enemy spawning fully modular

# ECS ZONE UNIFICATION PATCH: All zones now fully ECS-managed entities

## Major Changes
- Added EnemyManager for centralized enemy creation
- Enemies now use ECS components:
  - TransformComponent for position
  - EnemyComponent for enemy-specific properties
  - HealthComponent for health management
  - CollisionComponent for hitboxes
  - StateComponent for behavior states
- Improved enemy initialization and management

## Benefits
- Consistent enemy creation through ECS
- Better type safety
- Improved error handling
- Cleaner code organization
- Easier to extend

## Usage
```python
# Create an enemy
enemy = enemy_manager.spawn_enemy(
    enemy_type="basic",
    x=100,
    y=100,
    health=100
)

# Enemies automatically have:
# - Position tracking
# - Health management
# - Collision detection
# - State management
```

## Implementation Details
- All enemies use ECS components
- Proper component initialization
- Type-safe component access
- Automatic cleanup
- Better error handling

# BULLET SYSTEM MIGRATION COMPLETE: Now fully ECS-compliant

## Major Changes
- Bullet system migrated to ECS architecture
- New components added:
  - BulletComponent: Tracks bullet-specific properties
  - DamageComponent: Handles damage values
  - VelocityComponent: Manages movement
  - LifetimeComponent: Controls bullet lifespan
- BulletManager rewritten to use ECS components
- New BulletSystem for processing bullets
- Removed legacy pygame.Sprite implementation

## Benefits
- Consistent with ECS architecture
- Better separation of concerns
- Improved performance
- Easier to extend and modify
- Better type safety

## Usage
```python
# Create a bullet
bullet = bullet_manager.create_bullet(
    x=100, y=100,
    dx=1, dy=0,
    damage=10,
    is_enemy=False
)

# BulletSystem automatically handles:
# - Position updates
# - Lifetime management
# - Entity cleanup
```

## Implementation Details
- All bullet properties are now components
- BulletSystem processes all bullet entities
- Automatic cleanup of expired bullets
- Proper component initialization
- Type-safe component access

# GRAND STABILIZATION PATCH: ECS entity creation fully centralized

## Major Changes
- Entity creation centralized through EntityManager.create_entity()
- TransformComponent automatically added to all entities
- UIManager and WorldManager properly injected with EntityManager
- Entity deserialization includes TransformComponent safety check
- Improved initialization order in main.py

## Benefits
- Consistent entity creation across all systems
- Guaranteed component initialization
- Better dependency injection
- Improved error handling
- Cleaner code organization

## Usage
```python
# Create entities through EntityManager
entity = entity_manager.create_entity(EntityType.PLAYER, "player1")

# Create UI elements
ui_element = ui_manager.create_element("button1", "button", (100, 100), (200, 50))

# Create world zones
zone = world_manager.create_zone("forest", (0, 0))
```

## Implementation Details
- All managers now require EntityManager in constructor
- Entity creation always includes TransformComponent
- Component attachment is properly handled
- Parent-child relationships are maintained
- Type safety is improved

# Refactor: UIManager now fully injected with EntityManager — ECS integrity enforced

## UIManager Changes
- UIManager now requires EntityManager in constructor
- All UI elements are created through EntityManager.create_entity()
- UIComponent is properly attached to entities
- Improved parent-child relationship handling
- Better type safety with Optional[str] for element IDs

## Benefits
- Consistent entity creation through EntityManager
- Guaranteed component initialization
- Better dependency injection
- Improved error handling
- Cleaner code organization

## Usage
```python
# Initialize UIManager with EntityManager
entity_manager = EntityManager()
ui_manager = UIManager(entity_manager)

# Create UI elements
button = ui_manager.create_element("button1", "button", (100, 100), (200, 50))
panel = ui_manager.create_element("panel1", "panel", (0, 0), (800, 600))
```

# Refactor: ECS entity creation centralized + TransformComponent safeguard added

## Entity Creation Changes
- All entity creation is now centralized through `EntityManager.create_entity()`
- TransformComponent is automatically added to all entities
- Entity deserialization includes TransformComponent safety check
- UI elements now use proper entity creation through EntityManager

## Benefits
- Consistent entity initialization
- Guaranteed TransformComponent presence
- Reduced code duplication
- Better error handling
- Improved maintainability

## Usage
```python
# Create an entity
entity = entity_manager.create_entity(EntityType.PLAYER, "player1")

# Create a UI element
ui_element = ui_manager.create_element("button1", "button", (100, 100), (200, 50))
```

# Refactor: Deprecated systems removed (TilesetManager, StructuredZoneGenerator, StateHistory)

# ZONE TEMPLATE LOADER FULLY REFACTORED: Nested biome/zone_type indexing now stable

# ZONE ENTITY SPAWNING FIX: Zones now fully ECS-compliant

## Major Changes
- Added ZoneEntitySpawner system for ECS-compliant entity creation
- Updated ZoneTemplateLoader to use EntityManager
- Removed legacy entity dicts from zone templates
- Improved entity component initialization
- Better separation of concerns

## Benefits
- Consistent entity creation through ECS
- Better type safety
- Improved error handling
- Cleaner code organization
- Easier to extend

## Usage
```python
# Create a zone with entities
zone_template = zone_template_loader.get_template("forest", "zone1")
zone_entity_spawner.spawn_zone_entities(zone_template)

# Entities are created with proper components:
# - TransformComponent for position
# - CollisionComponent for hitboxes
# - Type-specific components (EnemyComponent, LootComponent, etc.)
```

## Implementation Details
- All zone entities use ECS components
- Proper component initialization
- Type-safe component access
- Automatic cleanup
- Better error handling

# COMPONENT CRADLE BUILT: All ECS components fully defined

# Bullet Hell Game

A fast-paced 2D bullet hell game built with Pygame.

## Features

- Fast-paced combat with bullet patterns
- Grappling hook mechanics for movement
- Multiple enemy types with different behaviors
- Wave-based enemy spawning system
- Platform-based level design
- Health and damage system
- State management (menu, playing, paused, game over)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bullet-hell-game.git
cd bullet-hell-game
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

To start the game:
```bash
python main.py
```

## Controls

- WASD/Arrow Keys: Movement
- Space: Jump
- Left Mouse Button: Shoot
- Right Mouse Button: Grappling Hook
- W/S while grappling: Extend/Retract hook
- ESC: Pause game

## Development

### Project Structure

- `main.py`: Main game loop and initialization
- `config.py`: Game configuration and constants
- `game_state.py`: State management system
- `player.py`: Player class and mechanics
- `enemies.py`: Enemy types and management
- `bullets.py`: Bullet system
- `tiles.py`: Platform and tile management
- `logging_config.py`: Logging configuration

### Running Tests

To run the test suite:
```bash
pytest
```

For test coverage report:
```bash
pytest --cov=.
```

### Logging

Logs are stored in the `logs` directory with timestamps. The logging system provides:
- Console output for important messages
- Detailed file logging for debugging
- Different log levels (DEBUG, INFO, WARNING, ERROR)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# StateComponent created for FSM support

# SpriteComponent updated: ECS update() method added for consistency

# ZoneComponent created for zone-based world streaming

# Starting Zone Template Created for WorldManager

## Zone Structure
- Created default starting zone in `zones/forest/starting_zone.json`
- Basic forest biome with ground tiles
- Initial enemy spawns (grunt and tank)
- Ready for loot and decorations

## Usage
The starting zone template provides:
- 10x5 grid of ground tiles
- Two initial enemies for testing
- Empty arrays for future loot and decorations

# AssetManager load_all() implemented: Centralized asset loading enabled

# BACKGROUND TILESET INTEGRATION COMPLETE: Biome tiles now ready for rendering

The game now supports a comprehensive background tileset system with the following features:

## Tileset Details
- Image dimensions: 512x128
- Tile size: 32x32
- Total tiles: 16 (4 columns x 4 rows)
- Organized top-left to bottom-right

## Biome Layout
- Grassland: Tiles 0-3 (Row 0)
- Lava: Tiles 4-7 (Row 1)
- Tech: Tiles 8-11 (Row 2)
- Ice: Tiles 12-15 (Row 3)

## Usage
The background tiles can be accessed through the `AssetManager`:
```python
# Get a specific tile
tile = asset_manager.tiles.get_tile('grass', 0)  # Gets first grassland tile
tile = asset_manager.tiles.get_tile('lava', 2)   # Gets third lava tile
tile = asset_manager.tiles.get_tile('tech', 1)   # Gets second tech tile
tile = asset_manager.tiles.get_tile('ice', 3)    # Gets fourth ice tile
```

The renderer automatically handles background tile rendering with parallax effects.
