#!/usr/bin/env python3
"""
Lead Scraper Bot
A Python-based bot for scraping business leads from various sources.

Features:
- Minimal UI for task management
- Local MongoDB database for data storage
- Google Maps and Yelp scraping
- Excel export functionality
- Real-time task status tracking
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui import MainApplication

def main():
    """Main entry point for the Lead Scraper Bot"""
    try:
        app = MainApplication()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
