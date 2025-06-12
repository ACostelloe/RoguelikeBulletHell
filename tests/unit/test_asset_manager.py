"""
Unit tests for the AssetManager class.
"""
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from asset_manager import AssetManager

class TestAssetManager(unittest.TestCase):
    """Test cases for the AssetManager class."""
    
    def setUp(self):
        """Set up each test case."""
        self.asset_manager = AssetManager.get_instance(asset_dir="tests/assets")
    
    def test_asset_loading(self):
        """Test that assets can be indexed without exceptions."""
        self.asset_manager.load_all()  # Use the real method for asset loading
    
    def test_cleanup(self):
        """Test that cleanup can be called without exceptions."""
        self.asset_manager.cleanup()  # Should not raise

if __name__ == '__main__':
    unittest.main() 