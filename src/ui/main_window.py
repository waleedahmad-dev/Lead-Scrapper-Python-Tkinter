import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
from typing import Dict, List
from src.database import DatabaseManager
from src.scraper import TaskManager
from .widgets import TaskForm, ResultsViewer, StatusBar
from config.config import Config

class MainApplication:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.db_manager = None
        self.task_manager = None
        
        self.setup_logging()
        self.setup_database()
        self.setup_ui()
        self.load_tasks()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('lead_scraper.log'),
                logging.StreamHandler()
            ]
        )
    
    def setup_database(self):
        """Setup database connection"""
        try:
            self.db_manager = DatabaseManager()
            self.task_manager = TaskManager(self.db_manager)
            logging.info("Database connection established")
        except Exception as e:
            messagebox.showerror("Database Error", 
                               f"Failed to connect to database:\n{str(e)}\n\n"
                               "Please ensure MongoDB is running.")
            self.root.quit()
    
    def setup_ui(self):
        """Setup the main user interface"""
        self.root.title("Lead Scraper Bot")
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Toolbar
        self.setup_toolbar(main_container)
        
        # Main content area
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Tasks list
        self.setup_tasks_list(content_frame)
        
        # Status bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_toolbar(self, parent):
        """Setup toolbar with buttons"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # New task button
        ttk.Button(toolbar, text="New Task", 
                  command=self.create_new_task).pack(side=tk.LEFT, padx=(0, 5))
        
        # Refresh button
        ttk.Button(toolbar, text="Refresh", 
                  command=self.load_tasks).pack(side=tk.LEFT, padx=5)
        
        # Delete task button
        ttk.Button(toolbar, text="Delete Task", 
                  command=self.delete_task).pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # View results button
        ttk.Button(toolbar, text="View Results", 
                  command=self.view_results).pack(side=tk.LEFT, padx=5)
        
        # Export results button
        ttk.Button(toolbar, text="Export All Results", 
                  command=self.export_all_results).pack(side=tk.LEFT, padx=5)
    
    def setup_tasks_list(self, parent):
        """Setup tasks list with treeview"""
        # Tasks frame
        tasks_frame = ttk.LabelFrame(parent, text="Tasks", padding="10")
        tasks_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid
        tasks_frame.grid_rowconfigure(0, weight=1)
        tasks_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview for tasks
        columns = ('keyword', 'location', 'status', 'results_count', 'created_at')
        self.tasks_tree = ttk.Treeview(tasks_frame, columns=columns, show='headings')
        
        # Define headings
        self.tasks_tree.heading('keyword', text='Keyword')
        self.tasks_tree.heading('location', text='Location')
        self.tasks_tree.heading('status', text='Status')
        self.tasks_tree.heading('results_count', text='Results')
        self.tasks_tree.heading('created_at', text='Created')
        
        # Configure column widths
        self.tasks_tree.column('keyword', width=200)
        self.tasks_tree.column('location', width=200)
        self.tasks_tree.column('status', width=100)
        self.tasks_tree.column('results_count', width=80)
        self.tasks_tree.column('created_at', width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tasks_frame, orient=tk.VERTICAL, command=self.tasks_tree.yview)
        h_scrollbar = ttk.Scrollbar(tasks_frame, orient=tk.HORIZONTAL, command=self.tasks_tree.xview)
        self.tasks_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tasks_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Context menu
        self.setup_context_menu()
        
        # Double-click to view results
        self.tasks_tree.bind('<Double-1>', lambda e: self.view_results())
    
    def setup_context_menu(self):
        """Setup right-click context menu"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="View Results", command=self.view_results)
        self.context_menu.add_command(label="Start Task", command=self.start_task)
        self.context_menu.add_command(label="Stop Task", command=self.stop_task)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Task", command=self.delete_task)
        
        # Bind right-click
        self.tasks_tree.bind('<Button-3>', self.show_context_menu)
    
    def show_context_menu(self, event):
        """Show context menu"""
        # Select item under cursor
        item = self.tasks_tree.identify_row(event.y)
        if item:
            self.tasks_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def create_new_task(self):
        """Create a new scraping task"""
        def on_task_created(task_data):
            try:
                # Create task in database
                task_id = self.db_manager.create_task(
                    task_data['keyword'], 
                    task_data['location']
                )
                
                # Start the task
                self.task_manager.start_task(
                    task_id,
                    task_data['keyword'],
                    task_data['location'],
                    task_data['scraper_type'],
                    self.on_task_event
                )
                
                # Refresh tasks list
                self.load_tasks()
                self.status_bar.set_status(f"Started task: {task_data['keyword']} in {task_data['location']}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create task:\n{str(e)}")
        
        TaskForm(self.root, on_task_created)
    
    def start_task(self):
        """Start selected task"""
        selected = self.get_selected_task()
        if not selected:
            return
        
        task_id, task_data = selected
        
        if self.task_manager.is_task_running(task_id):
            messagebox.showwarning("Warning", "Task is already running")
            return
        
        if task_data['status'] in ['Running', 'Completed']:
            response = messagebox.askyesno("Confirm", 
                                        "Task has already been run. Start again?")
            if not response:
                return
        
        try:
            # Clear previous results
            self.db_manager.clear_task_results(task_id)
            
            # Start task
            self.task_manager.start_task(
                task_id,
                task_data['keyword'],
                task_data['location'],
                'google_maps',  # Default scraper
                self.on_task_event
            )
            
            self.load_tasks()
            self.status_bar.set_status(f"Started task: {task_data['keyword']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start task:\n{str(e)}")
    
    def stop_task(self):
        """Stop selected task"""
        selected = self.get_selected_task()
        if not selected:
            return
        
        task_id, task_data = selected
        
        if not self.task_manager.is_task_running(task_id):
            messagebox.showwarning("Warning", "Task is not running")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to stop this task?"):
            self.task_manager.stop_task(task_id)
            self.load_tasks()
            self.status_bar.set_status(f"Stopped task: {task_data['keyword']}")
    
    def delete_task(self):
        """Delete selected task"""
        selected = self.get_selected_task()
        if not selected:
            return
        
        task_id, task_data = selected
        
        if self.task_manager.is_task_running(task_id):
            messagebox.showwarning("Warning", "Cannot delete running task. Stop it first.")
            return
        
        if messagebox.askyesno("Confirm", 
                             f"Are you sure you want to delete the task '{task_data['keyword']}'?\n"
                             "This will also delete all associated results."):
            try:
                self.db_manager.delete_task(task_id)
                self.load_tasks()
                self.status_bar.set_status(f"Deleted task: {task_data['keyword']}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete task:\n{str(e)}")
    
    def view_results(self):
        """View results for selected task"""
        selected = self.get_selected_task()
        if not selected:
            return
        
        task_id, task_data = selected
        
        try:
            results = self.db_manager.get_task_results(task_id)
            if not results:
                messagebox.showinfo("Info", "No results available for this task")
                return
            
            ResultsViewer(self.root, results, task_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load results:\n{str(e)}")
    
    def export_all_results(self):
        """Export all results to Excel"""
        try:
            results = self.db_manager.get_all_results()
            if not results:
                messagebox.showinfo("Info", "No results to export")
                return
            
            ResultsViewer(self.root, results, {'keyword': 'All Results', 'location': 'All'})
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load results:\n{str(e)}")
    
    def get_selected_task(self):
        """Get selected task from tree"""
        selection = self.tasks_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task")
            return None
        
        item = selection[0]
        task_id = self.tasks_tree.item(item)['tags'][0] if self.tasks_tree.item(item)['tags'] else None
        
        if not task_id:
            messagebox.showerror("Error", "Invalid task selection")
            return None
        
        # Get task data from database
        task_data = self.db_manager.get_task(task_id)
        if not task_data:
            messagebox.showerror("Error", "Task not found in database")
            return None
        
        return task_id, task_data
    
    def load_tasks(self):
        """Load tasks from database into tree"""
        # Clear existing items
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
        
        try:
            tasks = self.db_manager.get_all_tasks()
            
            for task in tasks:
                # Format created date
                created_at = task['created_at'].strftime('%Y-%m-%d %H:%M')
                
                # Determine status color
                status = task['status']
                if self.task_manager.is_task_running(task['_id']):
                    status = 'Running'
                
                values = (
                    task['keyword'],
                    task['location'],
                    status,
                    task['results_count'],
                    created_at
                )
                
                # Add item with task_id as tag
                item = self.tasks_tree.insert('', tk.END, values=values, tags=(task['_id'],))
                
                # Set status-based styling
                if status == 'Running':
                    self.tasks_tree.set(item, 'status', '🔄 Running')
                elif status == 'Completed':
                    self.tasks_tree.set(item, 'status', '✅ Completed')
                elif status == 'Failed':
                    self.tasks_tree.set(item, 'status', '❌ Failed')
                elif status == 'Cancelled':
                    self.tasks_tree.set(item, 'status', '⏹️ Cancelled')
                else:
                    self.tasks_tree.set(item, 'status', '⏸️ Created')
            
            self.status_bar.set_status(f"Loaded {len(tasks)} tasks")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks:\n{str(e)}")
    
    def on_task_event(self, event: str, data: Dict):
        """Handle task events"""
        self.root.after(0, lambda: self._handle_task_event(event, data))
    
    def _handle_task_event(self, event: str, data: Dict):
        """Handle task events on main thread"""
        if event == "status_changed":
            self.load_tasks()
        elif event == "completed":
            self.load_tasks()
            results_count = len(data.get('results', []))
            self.status_bar.set_status(f"Task completed with {results_count} results")
        elif event == "failed":
            self.load_tasks()
            error = data.get('error', 'Unknown error')
            self.status_bar.set_status(f"Task failed: {error}")
            messagebox.showerror("Task Failed", f"Task failed with error:\n{error}")
        elif event == "cancelled":
            self.load_tasks()
            self.status_bar.set_status("Task cancelled")
    
    def on_closing(self):
        """Handle application closing"""
        if self.task_manager:
            running_tasks = self.task_manager.get_running_tasks()
            if running_tasks:
                if messagebox.askyesno("Confirm Exit", 
                                     f"There are {len(running_tasks)} running tasks. "
                                     "Do you want to stop them and exit?"):
                    self.task_manager.stop_all_tasks()
                else:
                    return
        
        if self.db_manager:
            self.db_manager.disconnect()
        
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()

def main():
    """Main entry point"""
    app = MainApplication()
    app.run()

if __name__ == "__main__":
    main()
