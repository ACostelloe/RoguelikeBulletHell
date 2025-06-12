class MockZoneTemplateLoader:
    def __init__(self):
        self.templates = ["forest", "cave", "boss"]
 
    def get_random_template(self, biome):
        return biome  # Simplified mock logic 