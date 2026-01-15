#!/usr/bin/env python3
"""
Simple test script to validate NLScraper structure
Run this AFTER installing dependencies: pip install -r requirements.txt
"""
import sys
import os

def test_imports():
    """Test if all modules can be imported"""
    print("Testing module imports...")
    
    try:
        import config
        print("✓ config module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False
    
    # Test if dependencies are installed
    try:
        import requests
        import pandas
        from bs4 import BeautifulSoup
        print("✓ Core dependencies available")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nPlease install dependencies first:")
        print("  pip install -r requirements.txt")
        return False
    
    try:
        import utils
        print("✓ utils module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import utils: {e}")
        return False
    
    try:
        import scraper
        print("✓ scraper module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import scraper: {e}")
        return False
    
    try:
        import image_downloader
        print("✓ image_downloader module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import image_downloader: {e}")
        return False
    
    try:
        import exporter
        print("✓ exporter module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import exporter: {e}")
        return False
    
    return True

def test_directories():
    """Test if required directories are created"""
    print("\nTesting directory creation...")
    
    import config
    
    dirs = [
        ('output', config.OUTPUT_DIR),
        ('images', config.IMAGES_DIR),
        ('checkpoints', config.CHECKPOINTS_DIR),
        ('logs', config.LOGS_DIR)
    ]
    
    all_exist = True
    for name, path in dirs:
        if os.path.exists(path):
            print(f"✓ {name} directory exists: {path}")
        else:
            print(f"✗ {name} directory missing: {path}")
            all_exist = False
    
    return all_exist

def test_config():
    """Test configuration values"""
    print("\nTesting configuration...")
    
    import config
    
    tests = [
        ('BASE_URL', hasattr(config, 'BASE_URL')),
        ('REQUEST_DELAY', hasattr(config, 'REQUEST_DELAY')),
        ('OUTPUT_FORMAT', hasattr(config, 'OUTPUT_FORMAT')),
        ('DOWNLOAD_IMAGES', hasattr(config, 'DOWNLOAD_IMAGES')),
    ]
    
    all_pass = True
    for name, result in tests:
        if result:
            print(f"✓ {name} is configured")
        else:
            print(f"✗ {name} is missing")
            all_pass = False
    
    return all_pass

def test_help_menu():
    """Test if help menu works"""
    print("\nTesting help menu...")
    
    try:
        import main
        print("✓ main module imported successfully")
        print("\nTo see the help menu, run:")
        print("  python main.py --help")
        return True
    except Exception as e:
        print(f"✗ Failed to import main: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("NLScraper Structure Validation")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_imports()))
    
    if results[0][1]:  # Only continue if imports work
        results.append(("Directory Creation", test_directories()))
        results.append(("Configuration", test_config()))
        results.append(("Help Menu", test_help_menu()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! NLScraper is ready to use.")
        print("\nQuick start:")
        print("  python main.py --max-products 5 --no-images")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the output above.")
        print("\nMake sure to install dependencies:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == '__main__':
    sys.exit(main())
