from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional
import logging
from config.config import Config

class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(Config.MONGODB_URI)
            self.db = self.client[Config.DATABASE_NAME]
            # Test connection
            self.client.admin.command('ping')
            logging.info("Connected to MongoDB successfully")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logging.info("Disconnected from MongoDB")
    
    def create_task(self, keyword: str, location: str) -> str:
        """Create a new scraping task"""
        task = {
            'keyword': keyword,
            'location': location,
            'status': 'Created',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'results_count': 0,
            'error_message': None
        }
        
        result = self.db.tasks.insert_one(task)
        logging.info(f"Created task {result.inserted_id} for keyword '{keyword}' in '{location}'")
        return str(result.inserted_id)
    
    def update_task_status(self, task_id: str, status: str, error_message: str = None):
        """Update task status"""
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow()
        }
        if error_message:
            update_data['error_message'] = error_message
        
        self.db.tasks.update_one(
            {'_id': task_id},
            {'$set': update_data}
        )
        logging.info(f"Updated task {task_id} status to {status}")
    
    def get_all_tasks(self) -> List[Dict]:
        """Get all tasks"""
        tasks = list(self.db.tasks.find().sort('created_at', -1))
        for task in tasks:
            task['_id'] = str(task['_id'])
        return tasks
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get a specific task"""
        task = self.db.tasks.find_one({'_id': task_id})
        if task:
            task['_id'] = str(task['_id'])
        return task
    
    def delete_task(self, task_id: str):
        """Delete a task and its associated results"""
        # Delete task results first
        self.db.results.delete_many({'task_id': task_id})
        # Delete task
        result = self.db.tasks.delete_one({'_id': task_id})
        if result.deleted_count > 0:
            logging.info(f"Deleted task {task_id} and its results")
        return result.deleted_count > 0
    
    def save_results(self, task_id: str, results: List[Dict]):
        """Save scraping results for a task"""
        if not results:
            return
        
        # Add task_id and timestamp to each result
        for result in results:
            result['task_id'] = task_id
            result['scraped_at'] = datetime.utcnow()
        
        # Insert results
        self.db.results.insert_many(results)
        
        # Update task results count
        self.db.tasks.update_one(
            {'_id': task_id},
            {
                '$set': {
                    'results_count': len(results),
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        logging.info(f"Saved {len(results)} results for task {task_id}")
    
    def get_task_results(self, task_id: str) -> List[Dict]:
        """Get results for a specific task"""
        results = list(self.db.results.find({'task_id': task_id}))
        for result in results:
            result['_id'] = str(result['_id'])
        return results
    
    def get_all_results(self) -> List[Dict]:
        """Get all results"""
        results = list(self.db.results.find().sort('scraped_at', -1))
        for result in results:
            result['_id'] = str(result['_id'])
        return results
    
    def clear_task_results(self, task_id: str):
        """Clear results for a specific task"""
        result = self.db.results.delete_many({'task_id': task_id})
        # Reset task results count
        self.db.tasks.update_one(
            {'_id': task_id},
            {
                '$set': {
                    'results_count': 0,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        logging.info(f"Cleared {result.deleted_count} results for task {task_id}")
        return result.deleted_count
