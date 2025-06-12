class MockAssetManager:
    def __init__(self):
        self.assets = {
            "player": "player.png",
            "enemies/basic": "basic.png",
            "enemies/elite": "elite.png"
        }

    def get_image(self, name):
        return self.assets.get(name, "mock_image.png")

    def has_image(self, name):
        return name in self.assets

    def load_assets(self, path):
        pass

    def verify_all_assets(self):
        return []  # Always valid for mock

    def cleanup(self):
        pass 