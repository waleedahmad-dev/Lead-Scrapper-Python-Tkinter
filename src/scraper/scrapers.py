import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import re
import logging
from typing import List, Dict
from config.config import Config
import googlemaps

class BaseScraper:
    """Base class for all scrapers"""
    
    def __init__(self):
        self.results = []
        self.delay = Config.SCRAPING_DELAY
        self.max_results = Config.MAX_RESULTS_PER_TASK
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def extract_email(self, text: str) -> str:
        """Extract email from text using regex"""
        if not text:
            return ""
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""
    
    def scrape(self, keyword: str, location: str) -> List[Dict]:
        """Abstract method to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement the scrape method")

class GoogleMapsScraper(BaseScraper):
    """Scraper for Google Maps using Selenium"""
    
    def __init__(self):
        super().__init__()
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with options"""
        try:
            chrome_options = Options()
            if Config.SELENIUM_HEADLESS:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logging.info("Chrome driver setup successfully")
        except Exception as e:
            logging.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    def scrape(self, keyword: str, location: str) -> List[Dict]:
        """Scrape Google Maps for businesses"""
        results = []
        
        try:
            # Construct search URL
            search_query = f"{keyword} in {location}"
            url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            logging.info(f"Scraping Google Maps for: {search_query}")
            self.driver.get(url)
            
            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[role="main"]'))
            )
            
            time.sleep(3)  # Additional wait for content to load
            
            # Find business listings
            business_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-result-index]')
            
            for i, element in enumerate(business_elements[:self.max_results]):
                try:
                    # Click on the business to get more details
                    element.click()
                    time.sleep(self.delay)
                    
                    # Extract business information
                    business_info = self.extract_business_info()
                    if business_info:
                        results.append(business_info)
                        logging.info(f"Scraped business: {business_info.get('name', 'Unknown')}")
                    
                except Exception as e:
                    logging.warning(f"Error scraping business {i}: {e}")
                    continue
            
            logging.info(f"Scraped {len(results)} businesses from Google Maps")
            
        except Exception as e:
            logging.error(f"Error during Google Maps scraping: {e}")
            raise
        
        return results
    
    def extract_business_info(self) -> Dict:
        """Extract business information from the current page"""
        try:
            business_info = {}
            
            # Business name
            try:
                name_element = self.driver.find_element(By.CSS_SELECTOR, 'h1[data-attrid="title"]')
                business_info['name'] = self.clean_text(name_element.text)
            except:
                try:
                    name_element = self.driver.find_element(By.CSS_SELECTOR, '[data-section-id="overview"] h1')
                    business_info['name'] = self.clean_text(name_element.text)
                except:
                    business_info['name'] = "Unknown"
            
            # Address
            try:
                address_element = self.driver.find_element(By.CSS_SELECTOR, '[data-item-id="address"]')
                business_info['address'] = self.clean_text(address_element.text)
            except:
                business_info['address'] = ""
            
            # Phone number
            try:
                phone_element = self.driver.find_element(By.CSS_SELECTOR, '[data-item-id="phone:tel:"]')
                business_info['phone'] = self.clean_text(phone_element.text)
            except:
                business_info['phone'] = ""
            
            # Website
            try:
                website_element = self.driver.find_element(By.CSS_SELECTOR, '[data-item-id="authority"]')
                business_info['website'] = self.clean_text(website_element.get_attribute('href'))
            except:
                business_info['website'] = ""
            
            # Try to get email from website if available
            business_info['email'] = ""
            if business_info.get('website'):
                business_info['email'] = self.scrape_email_from_website(business_info['website'])
            
            # Rating
            try:
                rating_element = self.driver.find_element(By.CSS_SELECTOR, '[data-value="Formatted rating"]')
                business_info['rating'] = self.clean_text(rating_element.text)
            except:
                business_info['rating'] = ""
            
            # Category
            try:
                category_element = self.driver.find_element(By.CSS_SELECTOR, '[data-section-id="overview"] button[jsaction*="category"]')
                business_info['category'] = self.clean_text(category_element.text)
            except:
                business_info['category'] = ""
            
            return business_info
            
        except Exception as e:
            logging.error(f"Error extracting business info: {e}")
            return {}
    
    def scrape_email_from_website(self, website_url: str) -> str:
        """Try to scrape email from business website"""
        try:
            if not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url
            
            response = requests.get(website_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for email in contact pages
                contact_links = soup.find_all('a', href=re.compile(r'contact|about', re.I))
                for link in contact_links[:3]:  # Check first 3 contact links
                    try:
                        contact_url = requests.compat.urljoin(website_url, link.get('href'))
                        contact_response = requests.get(contact_url, timeout=5)
                        if contact_response.status_code == 200:
                            email = self.extract_email(contact_response.text)
                            if email:
                                return email
                    except:
                        continue
                
                # Look for email in main page
                return self.extract_email(response.text)
            
        except Exception as e:
            logging.warning(f"Could not scrape email from {website_url}: {e}")
        
        return ""
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logging.info("Browser driver closed")

class YelpScraper(BaseScraper):
    """Scraper for Yelp using requests and BeautifulSoup"""
    
    def scrape(self, keyword: str, location: str) -> List[Dict]:
        """Scrape Yelp for businesses"""
        results = []
        
        try:
            # Construct search URL
            search_query = keyword.replace(' ', '+')
            location_query = location.replace(' ', '+')
            url = f"https://www.yelp.com/search?find_desc={search_query}&find_loc={location_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            logging.info(f"Scraping Yelp for: {keyword} in {location}")
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find business listings
                business_elements = soup.find_all('div', {'data-testid': 'serp-ia-card'})
                
                for element in business_elements[:self.max_results]:
                    try:
                        business_info = self.extract_yelp_business_info(element)
                        if business_info:
                            results.append(business_info)
                            logging.info(f"Scraped Yelp business: {business_info.get('name', 'Unknown')}")
                    
                    except Exception as e:
                        logging.warning(f"Error scraping Yelp business: {e}")
                        continue
                
                logging.info(f"Scraped {len(results)} businesses from Yelp")
            
            else:
                logging.error(f"Failed to fetch Yelp page: {response.status_code}")
        
        except Exception as e:
            logging.error(f"Error during Yelp scraping: {e}")
        
        return results
    
    def extract_yelp_business_info(self, element) -> Dict:
        """Extract business information from Yelp element"""
        try:
            business_info = {}
            
            # Business name
            name_element = element.find('a', {'data-analytics-label': 'biz-name'})
            business_info['name'] = self.clean_text(name_element.text) if name_element else "Unknown"
            
            # Address
            address_element = element.find('p', string=re.compile(r'.*\d.*'))
            business_info['address'] = self.clean_text(address_element.text) if address_element else ""
            
            # Phone (not usually available in search results)
            business_info['phone'] = ""
            
            # Website (not usually available in search results)
            business_info['website'] = ""
            
            # Email (not available in search results)
            business_info['email'] = ""
            
            # Rating
            rating_element = element.find('div', {'role': 'img'})
            if rating_element and 'aria-label' in rating_element.attrs:
                rating_text = rating_element['aria-label']
                rating_match = re.search(r'(\d+\.?\d*)\s*star', rating_text)
                business_info['rating'] = rating_match.group(1) if rating_match else ""
            else:
                business_info['rating'] = ""
            
            # Category
            category_elements = element.find_all('span', class_=re.compile(r'category'))
            if category_elements:
                categories = [self.clean_text(cat.text) for cat in category_elements]
                business_info['category'] = ', '.join(categories)
            else:
                business_info['category'] = ""
            
            return business_info
            
        except Exception as e:
            logging.error(f"Error extracting Yelp business info: {e}")
            return {}

class ScraperFactory:
    """Factory class to create appropriate scrapers"""
    
    @staticmethod
    def create_scraper(scraper_type: str = "google_maps") -> BaseScraper:
        """Create a scraper instance based on type"""
        if scraper_type == "google_maps":
            return GoogleMapsScraper()
        elif scraper_type == "yelp":
            return YelpScraper()
        else:
            raise ValueError(f"Unknown scraper type: {scraper_type}")
    
    @staticmethod
    def get_available_scrapers() -> List[str]:
        """Get list of available scraper types"""
        return ["google_maps", "yelp"]
