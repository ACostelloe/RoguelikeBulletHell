class MockZone:
    def __init__(self, biome):
        self.biome = biome
        self.width = 10
        self.height = 10
        self.layout = []

class MockWorldManager:
    def __init__(self):
        self.current_zone = None

    def generate_zone(self, biome_name):
        return MockZone(biome_name)

    def set_current_zone(self, zone):
        self.current_zone = zone

    def get_current_zone(self):
        return self.current_zone 

class DummyTemplate:
    def __init__(self, biome):
        self.biome = biome
        self.width = 10
        self.height = 10
        self.layout = [] 