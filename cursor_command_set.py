# 📁 cursor_commands/

# ---- 1. diagnostics/print_game_flow.py ----
# Adds diagnostic prints to key flow points

COMMAND = "Add print statements to trace main game loop, state transitions, and first 3 update cycles."

INSTRUCTIONS = """
1. Add print("🟢 Entered Game.run loop") at the start of Game.run.
2. Add print("🟣 StateManager state: ", self.state) after each state switch.
3. In the update() method of Game, print("🔄 Frame update") for the first 3 frames only.
4. In draw(), print("🖼️ Drawing screen") to confirm rendering is triggered.
"""

# ---- 2. fix/zone_tile_platform_flag.py ----
# Fixes the ZoneTile is_platform init conflict

COMMAND = "Fix ZoneTile is_platform to allow init parameter while keeping __post_init__ fallback."

INSTRUCTIONS = """
1. In zone_types.py, update ZoneTile:
   - Change `is_platform: bool = False` to `is_platform: Optional[bool] = None`
   - In __post_init__, set:
       if self.is_platform is None:
           self.is_platform = self.tile_type in PLATFORM_TILE_TYPES
"""

# ---- 3. refactor/entity_bullets.py ----
# Converts bullet system to EntityManager

COMMAND = "Refactor BulletManager to register all bullets with EntityManager."

INSTRUCTIONS = """
1. Add bullet.type = "bullet" to all bullet classes.
2. Register bullets using entity_manager.add(bullet).
3. Remove update logic from BulletManager (if any).
4. Let EntityManager handle bullet update and collision.
"""

# ---- 4. extend/zone_template_transitions.py ----
# Adds support for transition tiles in zone templates

COMMAND = "Add support for transitions in zone templates."

INSTRUCTIONS = """
1. In zone_types.py, define ZoneTransition dataclass:
   - type: str
   - x: int
   - y: int
   - target: str
2. In json_zone_loader.py, parse "transitions" list into ZoneTransition objects.
3. Store transitions in ZoneTemplate.transitions list.
4. Add debug overlay in WorldManager to show transition tiles (toggle with T).
"""

# ---- 5. create/entity_base.py ----
# Base class for all game entities

COMMAND = "Create a base Entity class for use by enemies, bullets, player, loot."

INSTRUCTIONS = """
1. Define Entity with:
   - self.rect, self.image, self.health, self.dead, self.velocity
   - update(), draw(), on_collision(), on_death(), etc.
2. Let Enemy and other classes inherit from Entity.
3. EntityManager assumes all managed entities are subclasses of Entity.
"""

# ---- 6. debug/noise_check.py ----
# Add try/except to noise.pnoise2 to avoid hanging

COMMAND = "Add protection around Perlin noise to prevent hangs."

INSTRUCTIONS = """
1. In WorldManager._get_noise_value:
   - Wrap noise.pnoise2 in try/except:
     try:
         return noise.pnoise2(x * scale, y * scale, base=self.seed % 1024)
     except Exception as e:
         print("⚠️ Noise generation error", e)
         return 0.5  # fallback value
"""

# ---- 7. devtools/debug_overlay_toggle.py ----
# Adds key toggle for zone info overlay

COMMAND = "Add debug overlay toggle with key D to show zone grid and template names."

INSTRUCTIONS = """
1. In WorldManager, add `self.show_debug_overlay = False`.
2. In handle_input(), toggle this flag with key D.
3. In draw(), if flag is set:
   - Draw grid lines between zones
   - Draw biome/template names at center of each zone
"""

# ---- 8. system/zone_template_loader.py ----
# Adds recursive loader for zone JSON templates by biome and type

COMMAND = "Create loader to cache zone templates by biome and type."

INSTRUCTIONS = """
1. Recursively load all *.json in zones/<biome>/.
2. Parse and store templates in dictionary:
   cache[biome][zone_type] = [ZoneTemplate, ZoneTemplate, ...]
3. Provide method get_random_template(biome, zone_type) -> ZoneTemplate
"""
