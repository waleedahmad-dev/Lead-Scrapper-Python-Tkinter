# Lead Scraper Bot

A Python-based lead scraping bot with a minimal UI for managing scraping tasks and exporting results.

## Features

- **Minimal UI**: Easy-to-use interface for creating and managing tasks
- **Task Management**: Create, start, stop, and delete scraping tasks
- **Real-time Status**: View task status (Running, Completed, Failed, etc.)
- **Database Storage**: Local MongoDB for storing tasks and scraped data
- **Multiple Sources**: Support for Google Maps and Yelp scraping
- **Excel Export**: Export scraped data to Excel files with preview
- **Location Selection**: Choose from predefined US cities
- **Email Extraction**: Attempts to find email addresses from business websites

## Requirements

- Python 3.7+
- MongoDB (local installation)
- Chrome browser (for Selenium)
- ChromeDriver (automatically managed by Selenium)

## Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Install and start MongoDB on your local machine
6. Configure settings in `.env` file (optional)

## Configuration

Edit the `.env` file to customize settings:

```env
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=lead_scraper
SELENIUM_HEADLESS=True
SCRAPING_DELAY=2
MAX_RESULTS_PER_TASK=50
```

## Usage

1. Start the application:

   ```bash
   python main.py
   ```

2. Create a new task:

   - Click "New Task" button
   - Enter a keyword (e.g., "restaurants", "toy stores")
   - Select a location from the dropdown
   - Choose scraper type (Google Maps or Yelp)
   - Click "Create Task"

3. The task will start automatically and you can monitor its progress

4. View results:
   - Select a completed task
   - Click "View Results" or double-click the task
   - Preview the scraped data
   - Export to Excel if needed

## Scraped Data Fields

- **Business Name**: Name of the business
- **Address**: Physical address
- **Phone**: Phone number (if available)
- **Email**: Email address (if found on website)
- **Website**: Business website URL
- **Rating**: Customer rating
- **Category**: Business category/type

## Supported Locations

The bot includes 20 major US cities:

- New York, NY
- Los Angeles, CA
- Chicago, IL
- Houston, TX
- And more...

## File Structure

```
Lead-Scrapper/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── .env                   # Environment configuration
├── config/
│   └── config.py          # Application configuration
├── src/
│   ├── database/          # Database management
│   ├── scraper/           # Scraping logic
│   └── ui/                # User interface
└── exports/               # Excel export directory
```

## Troubleshooting

### MongoDB Connection Issues

- Ensure MongoDB is installed and running
- Check the connection string in `.env`
- Verify MongoDB is accessible on localhost:27017

### Chrome/ChromeDriver Issues

- Chrome browser must be installed
- ChromeDriver is automatically managed by Selenium
- If issues persist, try updating Chrome browser

### Scraping Issues

- Some websites may block automated scraping
- Adjust `SCRAPING_DELAY` in `.env` for slower scraping
- Use headless mode (`SELENIUM_HEADLESS=True`) for better performance

## Legal Notice

This tool is for educational and research purposes. Always comply with website terms of service and applicable laws when scraping data. Be respectful of rate limits and server resources.

## License

This project is provided as-is for educational purposes.
