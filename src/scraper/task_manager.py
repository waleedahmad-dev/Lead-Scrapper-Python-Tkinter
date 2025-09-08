import threading
import logging
from typing import Callable, Dict, List
from src.database import DatabaseManager
from .scrapers import ScraperFactory

class TaskManager:
    """Manages scraping tasks and their execution"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.running_tasks = {}  # task_id -> thread
        self.task_callbacks = {}  # task_id -> callback function
    
    def start_task(self, task_id: str, keyword: str, location: str, 
                   scraper_type: str = "google_maps", 
                   callback: Callable = None):
        """Start a scraping task in a separate thread"""
        
        if task_id in self.running_tasks:
            logging.warning(f"Task {task_id} is already running")
            return False
        
        # Store callback for this task
        if callback:
            self.task_callbacks[task_id] = callback
        
        # Create and start thread
        thread = threading.Thread(
            target=self._execute_task,
            args=(task_id, keyword, location, scraper_type),
            daemon=True
        )
        
        self.running_tasks[task_id] = thread
        thread.start()
        
        logging.info(f"Started task {task_id} for '{keyword}' in '{location}'")
        return True
    
    def _execute_task(self, task_id: str, keyword: str, location: str, scraper_type: str):
        """Execute a scraping task"""
        scraper = None
        
        try:
            # Update task status to running
            self.db_manager.update_task_status(task_id, "Running")
            self._notify_callback(task_id, "status_changed", {"status": "Running"})
            
            # Create and run scraper
            scraper = ScraperFactory.create_scraper(scraper_type)
            results = scraper.scrape(keyword, location)
            
            # Save results to database
            if results:
                self.db_manager.save_results(task_id, results)
                self.db_manager.update_task_status(task_id, "Completed")
                self._notify_callback(task_id, "completed", {"results": results})
                logging.info(f"Task {task_id} completed successfully with {len(results)} results")
            else:
                self.db_manager.update_task_status(task_id, "Completed", "No results found")
                self._notify_callback(task_id, "completed", {"results": []})
                logging.info(f"Task {task_id} completed with no results")
        
        except Exception as e:
            error_message = str(e)
            self.db_manager.update_task_status(task_id, "Failed", error_message)
            self._notify_callback(task_id, "failed", {"error": error_message})
            logging.error(f"Task {task_id} failed: {error_message}")
        
        finally:
            # Clean up
            if scraper and hasattr(scraper, 'close'):
                scraper.close()
            
            # Remove from running tasks
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            
            # Remove callback
            if task_id in self.task_callbacks:
                del self.task_callbacks[task_id]
    
    def _notify_callback(self, task_id: str, event: str, data: Dict):
        """Notify callback function about task events"""
        if task_id in self.task_callbacks:
            try:
                self.task_callbacks[task_id](event, data)
            except Exception as e:
                logging.error(f"Error in task callback for {task_id}: {e}")
    
    def stop_task(self, task_id: str):
        """Stop a running task (Note: This is not immediately effective due to thread limitations)"""
        if task_id in self.running_tasks:
            # Mark task as cancelled in database
            self.db_manager.update_task_status(task_id, "Cancelled")
            self._notify_callback(task_id, "cancelled", {})
            
            # Remove from running tasks
            del self.running_tasks[task_id]
            logging.info(f"Task {task_id} marked as cancelled")
            return True
        return False
    
    def is_task_running(self, task_id: str) -> bool:
        """Check if a task is currently running"""
        return task_id in self.running_tasks and self.running_tasks[task_id].is_alive()
    
    def get_running_tasks(self) -> List[str]:
        """Get list of currently running task IDs"""
        return [task_id for task_id, thread in self.running_tasks.items() if thread.is_alive()]
    
    def stop_all_tasks(self):
        """Stop all running tasks"""
        for task_id in list(self.running_tasks.keys()):
            self.stop_task(task_id)
