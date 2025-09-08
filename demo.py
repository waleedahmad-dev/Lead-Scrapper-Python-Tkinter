"""
Demo script for Lead Scraper Bot
This script demonstrates the core functionality without the UI
"""

import sys
import os
import time
import logging

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import DatabaseManager
from src.scraper import ScraperFactory, TaskManager

def setup_logging():
    """Setup logging for demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def demo_yelp_scraping():
    """Demonstrate Yelp scraping (safer, no browser required)"""
    print("🔍 Demo: Yelp Scraping")
    print("=" * 30)
    
    try:
        # Create Yelp scraper
        scraper = ScraperFactory.create_scraper("yelp")
        
        # Scrape for restaurants in New York
        keyword = "restaurants"
        location = "New York, NY"
        
        print(f"Searching for '{keyword}' in '{location}'...")
        results = scraper.scrape(keyword, location)
        
        print(f"\n📊 Found {len(results)} results:")
        print("-" * 50)
        
        for i, result in enumerate(results[:5], 1):  # Show first 5 results
            print(f"{i}. {result.get('name', 'Unknown')}")
            print(f"   Address: {result.get('address', 'N/A')}")
            print(f"   Rating: {result.get('rating', 'N/A')}")
            print(f"   Category: {result.get('category', 'N/A')}")
            print()
        
        if len(results) > 5:
            print(f"... and {len(results) - 5} more results")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return []

def demo_database_operations():
    """Demonstrate database operations"""
    print("\n💾 Demo: Database Operations")
    print("=" * 30)
    
    try:
        # Connect to database
        db = DatabaseManager()
        print("✅ Connected to database")
        
        # Create a demo task
        task_id = db.create_task("demo_restaurants", "New York, NY")
        print(f"✅ Created demo task: {task_id}")
        
        # Simulate some results
        demo_results = [
            {
                'name': 'Demo Restaurant 1',
                'address': '123 Main St, New York, NY',
                'phone': '(555) 123-4567',
                'email': 'info@demo1.com',
                'website': 'https://demo1.com',
                'rating': '4.5',
                'category': 'Italian'
            },
            {
                'name': 'Demo Restaurant 2',
                'address': '456 Broadway, New York, NY',
                'phone': '(555) 987-6543',
                'email': 'contact@demo2.com',
                'website': 'https://demo2.com',
                'rating': '4.2',
                'category': 'Mexican'
            }
        ]
        
        # Save results
        db.save_results(task_id, demo_results)
        print(f"✅ Saved {len(demo_results)} demo results")
        
        # Retrieve and display results
        saved_results = db.get_task_results(task_id)
        print(f"✅ Retrieved {len(saved_results)} results from database")
        
        # Update task status
        db.update_task_status(task_id, "Completed")
        print("✅ Updated task status to Completed")
        
        # Get all tasks
        all_tasks = db.get_all_tasks()
        print(f"✅ Total tasks in database: {len(all_tasks)}")
        
        # Clean up demo task
        db.delete_task(task_id)
        print("✅ Cleaned up demo task")
        
        db.disconnect()
        print("✅ Disconnected from database")
        
    except Exception as e:
        print(f"❌ Database demo error: {e}")

def demo_task_manager():
    """Demonstrate task manager"""
    print("\n⚙️ Demo: Task Manager")
    print("=" * 30)
    
    try:
        db = DatabaseManager()
        task_manager = TaskManager(db)
        
        # Create a task
        task_id = db.create_task("demo_task_manager", "Chicago, IL")
        print(f"✅ Created task for task manager demo: {task_id}")
        
        # Define callback function
        def task_callback(event, data):
            print(f"📢 Task event: {event}")
            if event == "completed":
                results_count = len(data.get('results', []))
                print(f"   Results found: {results_count}")
            elif event == "failed":
                print(f"   Error: {data.get('error', 'Unknown')}")
        
        # Start task with Yelp scraper (safer for demo)
        print("🚀 Starting task with Yelp scraper...")
        success = task_manager.start_task(
            task_id, 
            "coffee shops", 
            "Chicago, IL", 
            "yelp", 
            task_callback
        )
        
        if success:
            print("✅ Task started successfully")
            
            # Wait a bit for the task to complete
            print("⏳ Waiting for task to complete...")
            time.sleep(10)
            
            # Check if task is still running
            if task_manager.is_task_running(task_id):
                print("⏹️ Task is still running, stopping for demo...")
                task_manager.stop_task(task_id)
            else:
                print("✅ Task completed")
        
        # Clean up
        db.delete_task(task_id)
        db.disconnect()
        
    except Exception as e:
        print(f"❌ Task manager demo error: {e}")

def main():
    """Run all demos"""
    print("🎭 Lead Scraper Bot Demo")
    print("=" * 40)
    print("This demo shows the core functionality without the UI")
    print()
    
    setup_logging()
    
    # Run demos
    demo_database_operations()
    demo_yelp_scraping()
    demo_task_manager()
    
    print("\n" + "=" * 40)
    print("🎉 Demo completed!")
    print("\nTo run the full application with UI:")
    print("   python main.py")
    print("\nTo run a simple test:")
    print("   python test.py")

if __name__ == "__main__":
    main()
