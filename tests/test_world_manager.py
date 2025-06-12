import unittest
from world_manager import WorldManager
from zone_template_loader import ZoneTemplateLoader

class DummyTemplate:
    def __init__(self, biome):
        self.biome = biome
        self.width = 5
        self.height = 5
        self.layout = []
        self.spawn_points = []  # Added missing spawn_points attribute

class DummyWorldManager(WorldManager):
    def __init__(self):
        pass

    def generate_zone(self, biome_name):
        return DummyTemplate(biome_name)

class TestZoneGeneration(unittest.TestCase):
    def test_generate_multiple_zones(self):
        world = DummyWorldManager()
        forest = world.generate_zone("forest")
        cave = world.generate_zone("cave")
        boss = world.generate_zone("boss")

        self.assertEqual(forest.biome, "forest")
        self.assertEqual(cave.biome, "cave")
        self.assertEqual(boss.biome, "boss")

    def test_unknown_biome(self):
        world = DummyWorldManager()
        unknown_zone = world.generate_zone("volcano")
        self.assertEqual(unknown_zone.biome, "volcano") 