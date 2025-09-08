# Lead Scraper Bot - Project Structure

## 📁 Directory Structure

```
Lead-Scrapper/
├── 📄 main.py                      # Main application entry point
├── 📄 setup.py                     # Setup and dependency checker
├── 📄 test.py                      # Test suite
├── 📄 demo.py                      # Demo script (CLI version)
├── 📄 run.bat                      # Windows launcher script
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env                         # Environment configuration
├── 📄 README.md                    # Main documentation
├── 📄 PROJECT_STRUCTURE.md         # This file
│
├── 📁 venv/                        # Python virtual environment
│
├── 📁 config/                      # Configuration files
│   └── 📄 config.py                # Application settings
│
├── 📁 src/                         # Source code
│   ├── 📄 __init__.py
│   ├── 📄 utils.py                 # Utility functions
│   │
│   ├── 📁 database/                # Database management
│   │   ├── 📄 __init__.py
│   │   └── 📄 db_manager.py        # MongoDB operations
│   │
│   ├── 📁 scraper/                 # Web scraping logic
│   │   ├── 📄 __init__.py
│   │   ├── 📄 scrapers.py          # Scraper implementations
│   │   └── 📄 task_manager.py      # Task management
│   │
│   └── 📁 ui/                      # User interface
│       ├── 📄 __init__.py
│       ├── 📄 main_window.py       # Main application window
│       └── 📄 widgets.py           # UI components
│
├── 📁 exports/                     # Excel export directory
├── 📁 logs/                        # Log files
└── 📄 lead_scraper.log            # Application log file
```

## 🧩 Component Overview

### Core Application (`main.py`)

- **Purpose**: Entry point for the application
- **Features**: Initializes the UI and starts the main application loop

### Configuration (`config/`)

- **config.py**: Contains all application settings including:
  - Database connection settings
  - UI dimensions and styling
  - Scraping parameters
  - Predefined location list

### Database Layer (`src/database/`)

- **db_manager.py**: MongoDB interface providing:
  - Task CRUD operations
  - Results storage and retrieval
  - Connection management
  - Data validation

### Scraping Engine (`src/scraper/`)

- **scrapers.py**: Web scraping implementations:

  - `BaseScraper`: Abstract base class
  - `GoogleMapsScraper`: Google Maps scraper using Selenium
  - `YelpScraper`: Yelp scraper using requests/BeautifulSoup
  - `ScraperFactory`: Factory for creating scraper instances

- **task_manager.py**: Task execution management:
  - Threaded task execution
  - Task lifecycle management
  - Callback system for UI updates
  - Error handling and recovery

### User Interface (`src/ui/`)

- **main_window.py**: Main application window:

  - Task list management
  - Toolbar and menu system
  - Event handling
  - Application lifecycle

- **widgets.py**: Reusable UI components:
  - `TaskForm`: Modal for creating new tasks
  - `ResultsViewer`: Results preview and export window
  - `StatusBar`: Application status display

### Utilities (`src/utils.py`)

- Common utility functions for:
  - Data validation and cleaning
  - File operations
  - Excel export functionality
  - Text processing

## 🔄 Application Flow

1. **Startup**

   - Load configuration from `.env` and `config.py`
   - Connect to MongoDB database
   - Initialize UI components
   - Load existing tasks from database

2. **Task Creation**

   - User opens task creation form
   - Validates input (keyword, location, scraper type)
   - Creates task record in database
   - Automatically starts task execution

3. **Task Execution**

   - Task manager creates background thread
   - Initializes appropriate scraper (Google Maps/Yelp)
   - Scrapes data according to parameters
   - Saves results to database
   - Updates task status and UI

4. **Results Management**
   - User can view results in preview window
   - Export results to Excel format
   - Filter and sort results
   - Manage task lifecycle

## 🛠️ Key Features Implementation

### Multi-threaded Scraping

- Tasks run in separate threads to keep UI responsive
- Thread-safe database operations
- Callback system for real-time status updates

### Robust Error Handling

- Try-catch blocks around all major operations
- Graceful degradation when services are unavailable
- User-friendly error messages

### Flexible Scraper Architecture

- Factory pattern for easy scraper addition
- Consistent interface across different scrapers
- Configurable scraping parameters

### Data Export

- Excel export with formatting
- Configurable column selection
- Automatic file naming with timestamps

### UI/UX Features

- Real-time task status updates
- Context menus for quick actions
- Keyboard shortcuts
- Responsive design

## 🧪 Testing and Validation

### Setup Script (`setup.py`)

- Validates Python version
- Checks MongoDB connectivity
- Verifies Chrome browser installation
- Creates necessary directories
- Installs dependencies

### Test Suite (`test.py`)

- Import validation
- Configuration testing
- Database connectivity
- Scraper factory testing
- Utility function validation

### Demo Script (`demo.py`)

- CLI-based demonstration
- Shows core functionality without UI
- Safe testing without browser dependencies

## 📊 Database Schema

### Tasks Collection

```json
{
  "_id": "ObjectId",
  "keyword": "string",
  "location": "string",
  "status": "Created|Running|Completed|Failed|Cancelled",
  "created_at": "datetime",
  "updated_at": "datetime",
  "results_count": "integer",
  "error_message": "string|null"
}
```

### Results Collection

```json
{
  "_id": "ObjectId",
  "task_id": "string",
  "name": "string",
  "address": "string",
  "phone": "string",
  "email": "string",
  "website": "string",
  "rating": "string",
  "category": "string",
  "scraped_at": "datetime"
}
```

## 🔧 Configuration Options

### Environment Variables (`.env`)

- `MONGODB_URI`: Database connection string
- `DATABASE_NAME`: MongoDB database name
- `SELENIUM_HEADLESS`: Run browser in headless mode
- `SCRAPING_DELAY`: Delay between requests (seconds)
- `MAX_RESULTS_PER_TASK`: Maximum results per scraping task

### UI Configuration

- Window dimensions and styling
- Available locations list
- Default scraper selection
- Export file formats

## 🚀 Deployment and Usage

### Quick Start

1. Run `python setup.py` to check dependencies
2. Run `python test.py` to validate setup
3. Run `python main.py` to start the application
4. Or use `run.bat` on Windows for automated setup

### Creating Tasks

1. Click "New Task" in the main window
2. Enter keyword (e.g., "restaurants", "toy stores")
3. Select location from dropdown
4. Choose scraper type (Google Maps recommended)
5. Task starts automatically and shows progress

### Viewing Results

1. Select completed task from list
2. Click "View Results" or double-click task
3. Preview results in table format
4. Export to Excel if needed

## 🔒 Legal and Ethical Considerations

- **Rate Limiting**: Built-in delays between requests
- **Respectful Scraping**: Follows robots.txt when possible
- **Educational Purpose**: Intended for learning and research
- **Compliance**: Users responsible for following website ToS

## 🔮 Future Enhancements

- Additional scraper sources (Facebook, LinkedIn)
- Advanced filtering and search capabilities
- Data deduplication and enrichment
- API integrations for enhanced data
- Scheduled/automated scraping
- Cloud deployment options
- Advanced analytics and reporting
