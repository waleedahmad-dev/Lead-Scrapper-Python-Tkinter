"""
Test script for Lead Scraper Bot
Run this to test the basic functionality
"""

import sys
import os
import logging
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.database import DatabaseManager
        print("✅ Database module imported")
    except ImportError as e:
        print(f"❌ Failed to import database module: {e}")
        return False
    
    try:
        from src.scraper import ScraperFactory, TaskManager
        print("✅ Scraper module imported")
    except ImportError as e:
        print(f"❌ Failed to import scraper module: {e}")
        return False
    
    try:
        from src.ui import MainApplication
        print("✅ UI module imported")
    except ImportError as e:
        print(f"❌ Failed to import UI module: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        from src.database import DatabaseManager
        db = DatabaseManager()
        print("✅ Database connection successful")
        
        # Test basic operations
        task_id = db.create_task("test_keyword", "test_location")
        print(f"✅ Created test task: {task_id}")
        
        task = db.get_task(task_id)
        if task:
            print("✅ Retrieved test task")
        
        db.delete_task(task_id)
        print("✅ Deleted test task")
        
        db.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_scraper_factory():
    """Test scraper factory"""
    print("\nTesting scraper factory...")
    
    try:
        from src.scraper import ScraperFactory
        
        # Test available scrapers
        scrapers = ScraperFactory.get_available_scrapers()
        print(f"✅ Available scrapers: {scrapers}")
        
        # Test creating Yelp scraper (doesn't require browser)
        yelp_scraper = ScraperFactory.create_scraper("yelp")
        print("✅ Created Yelp scraper")
        
        return True
        
    except Exception as e:
        print(f"❌ Scraper factory test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config.config import Config
        
        print(f"✅ MongoDB URI: {Config.MONGODB_URI}")
        print(f"✅ Database name: {Config.DATABASE_NAME}")
        print(f"✅ Window size: {Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        print(f"✅ Available locations: {len(Config.LOCATIONS)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_utils():
    """Test utility functions"""
    print("\nTesting utilities...")
    
    try:
        from src.utils import validate_email, clean_phone_number, sanitize_filename
        
        # Test email validation
        assert validate_email("test@example.com") == True
        assert validate_email("invalid-email") == False
        print("✅ Email validation works")
        
        # Test phone cleaning
        clean_phone = clean_phone_number("(555) 123-4567")
        print(f"✅ Phone cleaning: {clean_phone}")
        
        # Test filename sanitization
        clean_name = sanitize_filename("test<file>name?.txt")
        print(f"✅ Filename sanitization: {clean_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Utils test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Lead Scraper Bot Test Suite")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Utilities", test_utils),
        ("Scraper Factory", test_scraper_factory),
        ("Database Connection", test_database_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work correctly.")
        print("\nYou can now run the main application:")
        print("   python main.py")
    else:
        print("⚠️  Some tests failed. Please check the setup.")
        print("Run setup.py to ensure all dependencies are installed:")
        print("   python setup.py")

if __name__ == "__main__":
    main()
