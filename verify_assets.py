"""
Asset verification script.
"""
import os
import json
import logging
from typing import Dict, List, Tuple
from datetime import datetime

def setup_logging() -> logging.Logger:
    """Set up logging for asset verification."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"asset_verification_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("AssetVerification")

def verify_assets(asset_dir: str, manifest_path: str) -> Dict[str, List[str]]:
    """Verify all assets listed in the manifest.
    
    Args:
        asset_dir: Root directory containing all assets
        manifest_path: Path to the asset manifest file
        
    Returns:
        Dict[str, List[str]]: Dictionary of missing assets by type
    """
    logger = setup_logging()
    logger.info(f"Starting asset verification for {asset_dir}")
    
    # Load manifest
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load manifest: {str(e)}")
        return {}
        
    missing_assets = {
        "images": [],
        "sounds": [],
        "music": [],
        "fonts": [],
        "data": []
    }
    
    # Verify each asset type
    for asset_type, assets in manifest["assets"].items():
        logger.info(f"Verifying {asset_type}...")
        
        if asset_type == "images":
            verify_image_assets(assets, asset_dir, missing_assets, logger)
        elif asset_type == "sounds":
            verify_sound_assets(assets, asset_dir, missing_assets, logger)
        elif asset_type == "music":
            verify_music_assets(assets, asset_dir, missing_assets, logger)
        elif asset_type == "fonts":
            verify_font_assets(assets, asset_dir, missing_assets, logger)
        elif asset_type == "data":
            verify_data_assets(assets, asset_dir, missing_assets, logger)
            
    # Log results
    for asset_type, missing in missing_assets.items():
        if missing:
            logger.warning(f"Missing {asset_type}:")
            for item in missing:
                logger.warning(f"  - {item}")
        else:
            logger.info(f"All {asset_type} verified")
            
    return missing_assets

def verify_image_assets(assets: Dict, asset_dir: str, missing_assets: Dict[str, List[str]], logger: logging.Logger) -> None:
    """Verify image assets."""
    for category, items in assets.items():
        if isinstance(items, dict) and "path" in items:
            # Single image
            path = os.path.join(asset_dir, items["path"])
            if not os.path.exists(path):
                missing_assets["images"].append(f"{category}: {path}")
                logger.error(f"Missing image: {path}")
        else:
            # Category of images
            for name, item in items.items():
                path = os.path.join(asset_dir, item["path"])
                if not os.path.exists(path):
                    missing_assets["images"].append(f"{category}/{name}: {path}")
                    logger.error(f"Missing image: {path}")

def verify_sound_assets(assets: Dict, asset_dir: str, missing_assets: Dict[str, List[str]], logger: logging.Logger) -> None:
    """Verify sound assets."""
    for category, items in assets.items():
        for name, item in items.items():
            path = os.path.join(asset_dir, item["path"])
            if not os.path.exists(path):
                missing_assets["sounds"].append(f"{category}/{name}: {path}")
                logger.error(f"Missing sound: {path}")

def verify_music_assets(assets: Dict, asset_dir: str, missing_assets: Dict[str, List[str]], logger: logging.Logger) -> None:
    """Verify music assets."""
    for name, item in assets.items():
        path = os.path.join(asset_dir, item["path"])
        if not os.path.exists(path):
            missing_assets["music"].append(f"{name}: {path}")
            logger.error(f"Missing music: {path}")

def verify_font_assets(assets: Dict, asset_dir: str, missing_assets: Dict[str, List[str]], logger: logging.Logger) -> None:
    """Verify font assets."""
    for name, item in assets.items():
        path = os.path.join(asset_dir, item["path"])
        if not os.path.exists(path):
            missing_assets["fonts"].append(f"{name}: {path}")
            logger.error(f"Missing font: {path}")

def verify_data_assets(assets: Dict, asset_dir: str, missing_assets: Dict[str, List[str]], logger: logging.Logger) -> None:
    """Verify data assets."""
    for category, items in assets.items():
        if isinstance(items, dict) and "path" in items:
            # Single data file
            path = os.path.join(asset_dir, items["path"])
            if not os.path.exists(path):
                missing_assets["data"].append(f"{category}: {path}")
                logger.error(f"Missing data file: {path}")
        else:
            # Category of data files
            for name, item in items.items():
                path = os.path.join(asset_dir, item["path"])
                if not os.path.exists(path):
                    missing_assets["data"].append(f"{category}/{name}: {path}")
                    logger.error(f"Missing data file: {path}")

if __name__ == "__main__":
    # Get the absolute path to the assets directory
    asset_dir = os.path.abspath("assets")
    manifest_path = os.path.join(asset_dir, "manifest.json")
    
    # Verify assets
    missing = verify_assets(asset_dir, manifest_path)
    
    # Print summary
    print("\nAsset Verification Summary:")
    print("==========================")
    for asset_type, items in missing.items():
        if items:
            print(f"\nMissing {asset_type}:")
            for item in items:
                print(f"  - {item}")
        else:
            print(f"\nAll {asset_type} verified") 