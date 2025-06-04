from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from abc import ABC, abstractmethod
import logging
import time
from urllib.parse import quote_plus
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper_test.log')
    ]
)
logger = logging.getLogger(__name__)

class ScraperStatus:
    """Track scraper status and statistics"""
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.last_error = None
        self.last_success = None
        self.average_response_time = 0
        self.total_response_time = 0
        self.results_found = 0
        self.last_url = None

    def to_dict(self) -> Dict:
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'last_error': str(self.last_error) if self.last_error else None,
            'last_success': self.last_success,
            'average_response_time': self.average_response_time,
            'results_found': self.results_found,
            'last_url': self.last_url
        }

class BaseScraper(ABC):
    """Base class for all scrapers"""
    
    def __init__(self):
        self.status = ScraperStatus()
        self.session = HTMLSession()  # Use HTMLSession for JavaScript support
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504]  # HTTP status codes to retry on
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
    
    @abstractmethod
    def search(self, query: str) -> List[Dict]:
        """Search the website and return results"""
        pass
    
    def make_request(self, url: str, render_js: bool = True) -> Optional[requests.Response]:
        """Make HTTP request with proper error handling and retry logic"""
        start_time = time.time()
        self.status.total_requests += 1
        self.status.last_url = url
        
        try:
            logger.info(f"Making request to: {url}")
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            if render_js:
                logger.info("Rendering JavaScript...")
                response.html.render(timeout=30)
                logger.info("JavaScript rendering completed")
            
            # Update status
            self.status.successful_requests += 1
            self.status.last_success = time.strftime('%Y-%m-%d %H:%M:%S')
            response_time = time.time() - start_time
            self.status.total_response_time += response_time
            self.status.average_response_time = self.status.total_response_time / self.status.successful_requests
            
            return response
            
        except Exception as e:
            self.status.failed_requests += 1
            self.status.last_error = str(e)
            logger.error(f"Request failed for {url}: {str(e)}")
            return None

class IkeaScraper(BaseScraper):
    """Scraper for IKEA website"""
    
    def search(self, query: str) -> List[Dict]:
        try:
            # Encode query for URL
            encoded_query = quote_plus(query)
            url = f"https://www.ikea.com/pl/pl/search/?q={encoded_query}"
            logger.info(f"Searching IKEA with URL: {url}")
            
            response = self.make_request(url, render_js=True)
            if not response:
                return []
            
            # Use BeautifulSoup for parsing the rendered HTML
            soup = BeautifulSoup(response.html.html, 'lxml')
            results = []
            
            # Find all product cards
            product_cards = soup.select('.pip-product-compact')
            logger.info(f"Found {len(product_cards)} product cards")
            
            for card in product_cards[:5]:  # Limit to 5 results per source
                try:
                    title_elem = card.select_one('.pip-header-section__title')
                    link_elem = card.select_one('a')
                    desc_elem = card.select_one('.pip-product-compact__rating-text')
                    price_elem = card.select_one('.pip-price__integer')
                    
                    if title_elem and link_elem:
                        title = title_elem.text.strip()
                        link = link_elem.get('href', '')
                        if not link.startswith('http'):
                            link = f"https://www.ikea.com{link}"
                        
                        result = {
                            'title': title,
                            'link': link,
                            'source': 'IKEA',
                            'snippet': desc_elem.text.strip() if desc_elem else '',
                            'price': price_elem.text.strip() if price_elem else ''
                        }
                        results.append(result)
                        self.status.results_found += 1
                        logger.info(f"Added IKEA result: {title}")
                except Exception as e:
                    logger.error(f"Error processing IKEA product card: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error scraping IKEA: {str(e)}")
            return []

class ManualslibScraper(BaseScraper):
    """Scraper for Manualslib website"""
    
    def search(self, query: str) -> List[Dict]:
        try:
            # Get first letter of query for URL
            first_letter = query[0].upper()
            encoded_query = quote_plus(query)
            url = f"https://www.manualslib.com/{first_letter}/{encoded_query}.html"
            logger.info(f"Searching Manualslib with URL: {url}")
            
            response = self.make_request(url, render_js=True)
            if not response:
                return []
            
            # Use BeautifulSoup for parsing the rendered HTML
            soup = BeautifulSoup(response.html.html, 'lxml')
            results = []
            
            # Find all manual entries
            manual_entries = soup.select('.mdl-left h3 a')
            logger.info(f"Found {len(manual_entries)} manual entries")
            
            for entry in manual_entries[:5]:  # Limit to 5 results per source
                try:
                    title = entry.text.strip()
                    link = entry.get('href', '')
                    if not link.startswith('http'):
                        link = f"https://www.manualslib.com{link}"
                    
                    # Try to get description from sibling div
                    desc_elem = entry.find_next_sibling('div')
                    
                    # Try to extract model number from title
                    model_number = None
                    if ' - ' in title:
                        model_number = title.split(' - ')[-1].strip()
                    
                    result = {
                        'title': title,
                        'link': link,
                        'source': 'Manualslib',
                        'snippet': desc_elem.text.strip() if desc_elem else '',
                        'model': model_number
                    }
                    results.append(result)
                    self.status.results_found += 1
                    logger.info(f"Added Manualslib result: {title}")
                except Exception as e:
                    logger.error(f"Error processing Manualslib entry: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error scraping Manualslib: {str(e)}")
            return []

class UnifiedScraper:
    """Manages multiple scrapers and combines their results"""
    
    def __init__(self):
        self.scrapers = {
            'IKEA': IkeaScraper(),
            'Manualslib': ManualslibScraper()
        }
    
    def search(self, query: str) -> List[Dict]:
        """
        Search across all configured scrapers and return combined results
        Returns max 10 deduplicated results
        """
        if not query.strip():
            logger.warning("Empty search query received")
            return []
            
        logger.info(f"Starting unified search for: {query}")
        all_results = []
        
        # Get results from all scrapers
        for scraper_name, scraper in self.scrapers.items():
            try:
                results = scraper.search(query)
                logger.info(f"Found {len(results)} results from {scraper_name}")
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Error with scraper {scraper_name}: {str(e)}")
        
        # Deduplicate results based on title
        seen_titles = set()
        unique_results = []
        
        for result in all_results:
            if result['title'] not in seen_titles:
                seen_titles.add(result['title'])
                unique_results.append(result)
                if len(unique_results) >= 10:  # Limit to 10 results
                    break
        
        logger.info(f"Returning {len(unique_results)} unique results")
        return unique_results
    
    def get_status(self) -> Dict:
        """Get status of all scrapers"""
        return {
            name: scraper.status.to_dict()
            for name, scraper in self.scrapers.items()
        } 