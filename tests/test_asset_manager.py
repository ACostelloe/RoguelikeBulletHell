import unittest
import os
import shutil
import json
from asset_manager import AssetManager

class TestAssetManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary test assets directory
        self.test_asset_dir = "tests/assets"
        os.makedirs(self.test_asset_dir, exist_ok=True)
        
        # Reset the singleton instance
        AssetManager._instance = None
        
        # Create the asset manager instance
        self.asset_manager = AssetManager.get_instance(asset_dir=self.test_asset_dir)

    def tearDown(self):
        # Clean up the test assets directory
        if os.path.exists(self.test_asset_dir):
            shutil.rmtree(self.test_asset_dir)
        
        # Reset the singleton instance
        AssetManager._instance = None

    def test_asset_loading(self):
        # Create a test asset index
        test_index = {
            "images": {},
            "sounds": {},
            "fonts": {},
            "music": {},
            "data": {}
        }
        
        # Save the test index
        index_path = os.path.join(self.test_asset_dir, "index.json")
        with open(index_path, "w") as f:
            json.dump(test_index, f)
        
        # Load the asset index
        self.asset_manager.load_asset_index()
        self.assertIsNotNone(self.asset_manager.asset_index)

    def test_cleanup(self):
        # Create some test assets
        test_image = os.path.join(self.test_asset_dir, "test.png")
        with open(test_image, "w") as f:
            f.write("test")
        
        # Load the test asset
        self.asset_manager.load_image("test", "test.png")
        
        # Clean up
        self.asset_manager.cleanup()
        self.assertEqual(len(self.asset_manager.images), 0) 