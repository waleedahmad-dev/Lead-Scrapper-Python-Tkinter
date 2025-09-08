import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
import os
from typing import List, Dict
from config.config import Config

class TaskForm(tk.Toplevel):
    """Form for creating new tasks"""
    
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.result = None
        
        self.title("Create New Task")
        self.geometry("400x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Keyword
        ttk.Label(main_frame, text="Keyword:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.keyword_var = tk.StringVar()
        keyword_entry = ttk.Entry(main_frame, textvariable=self.keyword_var, width=30)
        keyword_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        keyword_entry.focus()
        
        # Location
        ttk.Label(main_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.location_var = tk.StringVar()
        location_combo = ttk.Combobox(main_frame, textvariable=self.location_var, 
                                     values=Config.LOCATIONS, width=27, state="readonly")
        location_combo.grid(row=1, column=1, pady=5, padx=(10, 0))
        location_combo.set(Config.LOCATIONS[0])  # Default selection
        
        # Scraper type
        ttk.Label(main_frame, text="Scraper:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.scraper_var = tk.StringVar()
        scraper_combo = ttk.Combobox(main_frame, textvariable=self.scraper_var,
                                    values=["google_maps", "yelp"], width=27, state="readonly")
        scraper_combo.grid(row=2, column=1, pady=5, padx=(10, 0))
        scraper_combo.set("google_maps")  # Default selection
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Create Task", 
                  command=self.create_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to create task
        self.bind('<Return>', lambda e: self.create_task())
        self.bind('<Escape>', lambda e: self.cancel())
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def create_task(self):
        """Create the task"""
        keyword = self.keyword_var.get().strip()
        location = self.location_var.get()
        scraper_type = self.scraper_var.get()
        
        if not keyword:
            messagebox.showerror("Error", "Please enter a keyword")
            return
        
        if not location:
            messagebox.showerror("Error", "Please select a location")
            return
        
        self.result = {
            'keyword': keyword,
            'location': location,
            'scraper_type': scraper_type
        }
        
        if self.callback:
            self.callback(self.result)
        
        self.destroy()
    
    def cancel(self):
        """Cancel task creation"""
        self.result = None
        self.destroy()

class ResultsViewer(tk.Toplevel):
    """Window for viewing and previewing results"""
    
    def __init__(self, parent, results: List[Dict], task_info: Dict = None):
        super().__init__(parent)
        self.results = results
        self.task_info = task_info
        
        self.title("Results Preview")
        self.geometry("900x600")
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.center_window()
        self.load_results()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="Task Information", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        if self.task_info:
            info_text = f"Keyword: {self.task_info.get('keyword', 'N/A')} | " \
                       f"Location: {self.task_info.get('location', 'N/A')} | " \
                       f"Results: {len(self.results)}"
            ttk.Label(info_frame, text=info_text).grid(row=0, column=0, sticky=tk.W)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview for results
        columns = ('name', 'address', 'phone', 'email', 'website', 'rating', 'category')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.tree.heading('name', text='Business Name')
        self.tree.heading('address', text='Address')
        self.tree.heading('phone', text='Phone')
        self.tree.heading('email', text='Email')
        self.tree.heading('website', text='Website')
        self.tree.heading('rating', text='Rating')
        self.tree.heading('category', text='Category')
        
        # Configure column widths
        self.tree.column('name', width=150)
        self.tree.column('address', width=200)
        self.tree.column('phone', width=100)
        self.tree.column('email', width=150)
        self.tree.column('website', width=150)
        self.tree.column('rating', width=70)
        self.tree.column('category', width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(button_frame, text="Export to Excel", 
                  command=self.export_to_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def load_results(self):
        """Load results into the treeview"""
        for result in self.results:
            values = (
                result.get('name', ''),
                result.get('address', ''),
                result.get('phone', ''),
                result.get('email', ''),
                result.get('website', ''),
                result.get('rating', ''),
                result.get('category', '')
            )
            self.tree.insert('', tk.END, values=values)
    
    def export_to_excel(self):
        """Export results to Excel file"""
        if not self.results:
            messagebox.showwarning("Warning", "No results to export")
            return
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        keyword = self.task_info.get('keyword', 'results') if self.task_info else 'results'
        default_filename = f"{keyword.replace(' ', '_')}_{timestamp}.xlsx"
        
        # Ask user for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialdir=os.path.join(os.getcwd(), "exports"),
            initialfile=default_filename
        )
        
        if filename:
            try:
                # Create DataFrame
                df = pd.DataFrame(self.results)
                
                # Reorder columns for better readability
                column_order = ['name', 'address', 'phone', 'email', 'website', 'rating', 'category']
                existing_columns = [col for col in column_order if col in df.columns]
                df = df[existing_columns]
                
                # Export to Excel
                df.to_excel(filename, index=False, engine='openpyxl')
                
                messagebox.showinfo("Success", f"Results exported to:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results:\n{str(e)}")

class StatusBar(ttk.Frame):
    """Status bar widget"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        self.status_label = ttk.Label(self, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Progress bar (hidden by default)
        self.progress = ttk.Progressbar(self, mode='indeterminate')
        
    def set_status(self, message: str):
        """Set status message"""
        self.status_var.set(message)
    
    def show_progress(self):
        """Show and start progress bar"""
        self.progress.pack(side=tk.RIGHT, padx=5)
        self.progress.start()
    
    def hide_progress(self):
        """Hide and stop progress bar"""
        self.progress.stop()
        self.progress.pack_forget()
