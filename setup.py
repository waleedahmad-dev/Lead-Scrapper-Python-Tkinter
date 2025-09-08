"""
Setup script for Lead Scraper Bot
This script helps set up the environment and check dependencies
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True

def check_mongodb():
    """Check if MongoDB is accessible"""
    try:
        import pymongo
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("✅ MongoDB is running and accessible")
        client.close()
        return True
    except Exception as e:
        print("❌ MongoDB is not accessible")
        print(f"   Error: {e}")
        print("   Please install and start MongoDB")
        return False

def check_chrome():
    """Check if Chrome browser is installed"""
    try:
        if platform.system() == "Windows":
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
            chrome_found = any(os.path.exists(path) for path in chrome_paths)
        else:
            # For Linux/Mac, try to run chrome command
            result = subprocess.run(['which', 'google-chrome'], 
                                  capture_output=True, text=True)
            chrome_found = result.returncode == 0
        
        if chrome_found:
            print("✅ Chrome browser found")
            return True
        else:
            print("❌ Chrome browser not found")
            print("   Please install Google Chrome for web scraping")
            return False
    except Exception as e:
        print(f"❌ Error checking Chrome: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['exports', 'logs']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies"""
    try:
        print("Installing Python dependencies...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path('.env')
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    env_content = """# Environment configuration for Lead Scraper Bot
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=lead_scraper
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
SELENIUM_HEADLESS=True
SCRAPING_DELAY=2
MAX_RESULTS_PER_TASK=50
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with default settings")

def print_mongodb_instructions():
    """Print MongoDB installation instructions"""
    system = platform.system()
    
    print("\n📋 MongoDB Installation Instructions:")
    print("=" * 50)
    
    if system == "Windows":
        print("For Windows:")
        print("1. Download MongoDB Community Server from:")
        print("   https://www.mongodb.com/try/download/community")
        print("2. Run the installer and follow the setup wizard")
        print("3. Start MongoDB service:")
        print("   - Search for 'Services' in Start menu")
        print("   - Find 'MongoDB Server' and start it")
        print("4. Or use MongoDB Compass (GUI tool)")
    
    elif system == "Darwin":  # macOS
        print("For macOS:")
        print("1. Install using Homebrew:")
        print("   brew tap mongodb/brew")
        print("   brew install mongodb-community")
        print("2. Start MongoDB:")
        print("   brew services start mongodb/brew/mongodb-community")
    
    else:  # Linux
        print("For Linux (Ubuntu/Debian):")
        print("1. Import MongoDB public key:")
        print("   wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -")
        print("2. Add MongoDB repository:")
        print("   echo 'deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse' | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list")
        print("3. Install MongoDB:")
        print("   sudo apt-get update")
        print("   sudo apt-get install -y mongodb-org")
        print("4. Start MongoDB:")
        print("   sudo systemctl start mongod")

def main():
    """Main setup function"""
    print("🚀 Lead Scraper Bot Setup")
    print("=" * 30)
    
    all_good = True
    
    # Check Python version
    if not check_python_version():
        all_good = False
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        all_good = False
    
    # Check Chrome
    if not check_chrome():
        all_good = False
        print("   Chrome is required for Google Maps scraping")
    
    # Check MongoDB
    if not check_mongodb():
        all_good = False
        print_mongodb_instructions()
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 Setup completed successfully!")
        print("\nYou can now run the application with:")
        print("   python main.py")
    else:
        print("⚠️  Setup completed with warnings")
        print("Please address the issues above before running the application")
    
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
