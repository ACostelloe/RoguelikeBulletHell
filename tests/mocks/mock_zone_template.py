class DummyTemplate:
    def __init__(self, biome):
        self.biome = biome
        self.zone_type = "start"
        self.width = 10
        self.height = 10
        self.layout = [['.'] * 10 for _ in range(10)]
        self.tiles = []
        self.enemies = []
        self.loot = []
        self.decorations = []
        self.transitions = []
        self.name = f"{biome}_template"
        self.events = []
        self.spawn_zone = None
        self.transition_type = "" 