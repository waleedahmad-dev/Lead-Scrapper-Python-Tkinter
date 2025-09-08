import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'lead_scraper')
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
    SELENIUM_HEADLESS = os.getenv('SELENIUM_HEADLESS', 'True').lower() == 'true'
    SCRAPING_DELAY = int(os.getenv('SCRAPING_DELAY', '2'))
    MAX_RESULTS_PER_TASK = int(os.getenv('MAX_RESULTS_PER_TASK', '50'))
    
    # UI Configuration
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    
    # Locations for scraping
    LOCATIONS = [
        'New York, NY, USA',
        'Los Angeles, CA, USA',
        'Chicago, IL, USA',
        'Houston, TX, USA',
        'Phoenix, AZ, USA',
        'Philadelphia, PA, USA',
        'San Antonio, TX, USA',
        'San Diego, CA, USA',
        'Dallas, TX, USA',
        'San Jose, CA, USA',
        'Austin, TX, USA',
        'Jacksonville, FL, USA',
        'Fort Worth, TX, USA',
        'Columbus, OH, USA',
        'Charlotte, NC, USA',
        'San Francisco, CA, USA',
        'Indianapolis, IN, USA',
        'Seattle, WA, USA',
        'Denver, CO, USA',
        'Washington, DC, USA'
    ]
