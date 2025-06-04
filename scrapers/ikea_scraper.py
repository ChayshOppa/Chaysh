import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from scrapers.base_scraper import BaseScraper, ProductResult
import logging
import time
from urllib.parse import quote_plus
import random

logger = logging.getLogger(__name__)

class IkeaScraper(BaseScraper):
    """Scraper for IKEA website to find product manuals and information."""
    
    BASE_URL = "https://www.ikea.com"
    SEARCH_URL = f"{BASE_URL}/pl/pl/search/?q="  # Using Polish site as per rules
    
    # Common IKEA product series and their variants
    PRODUCT_SERIES = {
        'billy': {
            'name': 'BILLY',
            'type': 'bookcase',
            'variants': [
                {'name': 'Bookcase', 'model': '00263850', 'desc': 'Classic bookcase with adjustable shelves'},
                {'name': 'Bookcase with glass doors', 'model': '00263851', 'desc': 'Bookcase with glass doors for dust protection'},
                {'name': 'Bookcase with height extension', 'model': '00263852', 'desc': 'Bookcase with additional height unit'}
            ]
        },
        'malm': {
            'name': 'MALM',
            'type': 'bed',
            'variants': [
                {'name': 'Bed frame', 'model': '09046617', 'desc': 'Modern bed frame with headboard'},
                {'name': 'Bed frame with storage', 'model': '09046618', 'desc': 'Bed frame with storage drawers'},
                {'name': 'Bed frame with underbed storage', 'model': '09046619', 'desc': 'Bed frame with underbed storage boxes'}
            ]
        },
        'poang': {
            'name': 'POÄNG',
            'type': 'chair',
            'variants': [
                {'name': 'Armchair', 'model': '09128706', 'desc': 'Comfortable armchair with curved frame'},
                {'name': 'Rocking chair', 'model': '09128707', 'desc': 'Rocking chair for gentle motion'},
                {'name': 'Footstool', 'model': '09128708', 'desc': 'Matching footstool for relaxation'}
            ]
        },
        'kallax': {
            'name': 'KALLAX',
            'type': 'shelf',
            'variants': [
                {'name': 'Shelving unit', 'model': '80275887', 'desc': 'Versatile shelving unit with multiple compartments'},
                {'name': 'Shelving unit with inserts', 'model': '80275888', 'desc': 'Shelving unit with storage inserts'},
                {'name': 'Shelving unit with doors', 'model': '80275889', 'desc': 'Shelving unit with door inserts'}
            ]
        },
        'hemnes': {
            'name': 'HEMNES',
            'type': 'furniture',
            'variants': [
                {'name': 'Chest of drawers', 'model': '90246674', 'desc': 'Classic chest of drawers with 8 drawers'},
                {'name': 'TV unit', 'model': '90246675', 'desc': 'TV unit with storage and cable management'},
                {'name': 'Coffee table', 'model': '90246676', 'desc': 'Coffee table with storage shelf'}
            ]
        }
    }
    
    DUMMY_EXTRA_FIELDS = [
        'Material', 'Color', 'Dimensions', 'Weight', 'Max Load', 'Warranty', 'Country of Origin',
        'Assembly Required', 'Care Instructions', 'Sustainability'
    ]
    DUMMY_MATERIALS = ['Particleboard', 'Solid wood', 'Steel', 'Glass', 'Plastic']
    DUMMY_COLORS = ['White', 'Black', 'Oak', 'Birch', 'Gray', 'Blue']
    DUMMY_COUNTRIES = ['Poland', 'Sweden', 'Germany', 'China', 'Italy']
    
    def __init__(self, test_mode=False):
        super().__init__()
        self.test_mode = test_mode
        self.last_request_time = 0
        self.min_request_interval = 2  # Minimum seconds between requests
        # Add more headers to mimic a real browser
        self.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
    
    def _rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def _generate_dummy_results(self, query: str, max_results: int = 10) -> List[ProductResult]:
        query_lower = query.lower()
        results = []
        all_variants = []
        # Gather all possible variants
        for series_key, series_info in self.PRODUCT_SERIES.items():
            for variant in series_info['variants']:
                all_variants.append((series_info, variant))
        # If query matches a series, bias results toward that
        matching_variants = []
        for series_key, series_info in self.PRODUCT_SERIES.items():
            if series_key in query_lower or series_info['name'].lower() in query_lower:
                for variant in series_info['variants']:
                    matching_variants.append((series_info, variant))
        # Use matching or random variants
        chosen = matching_variants if matching_variants else all_variants
        chosen = random.sample(chosen, min(max_results, len(chosen)))
        for series_info, variant in chosen:
            # Generate 10 info fields
            info = {
                'Material': random.choice(self.DUMMY_MATERIALS),
                'Color': random.choice(self.DUMMY_COLORS),
                'Dimensions': f"{random.randint(60, 120)}x{random.randint(20, 50)}x{random.randint(80, 220)} cm",
                'Weight': f"{random.randint(10, 60)} kg",
                'Max Load': f"{random.randint(20, 50)} kg",
                'Warranty': f"{random.choice([2, 5])} years",
                'Country of Origin': random.choice(self.DUMMY_COUNTRIES),
                'Assembly Required': random.choice(['Yes', 'No']),
                'Care Instructions': random.choice(['Wipe clean with a damp cloth', 'Use mild cleaner', 'Do not bleach']),
                'Sustainability': random.choice(['Renewable material', 'Recyclable', 'Low formaldehyde'])
            }
            title = f"{series_info['name']} {variant['name']}"
            link = f"{self.BASE_URL}/pl/pl/p/{series_info['name'].lower()}-{variant['name'].lower().replace(' ', '-')}-{variant['model']}/"
            snippet = f"{variant['desc']} | Material: {info['Material']}, Color: {info['Color']}, Size: {info['Dimensions']}"
            # Add all info fields to snippet for display
            full_snippet = snippet + \
                f" | Weight: {info['Weight']}, Max Load: {info['Max Load']}, Warranty: {info['Warranty']}, " \
                f"Country: {info['Country of Origin']}, Assembly: {info['Assembly Required']}, " \
                f"Care: {info['Care Instructions']}, Sustainability: {info['Sustainability']}"
            result = ProductResult(
                title=title,
                snippet=full_snippet,
                source='ikea',
                links=[link],
                model=variant['model']
            )
            results.append(result)
        return results
    
    def search(self, query: str, max_results: int = 10) -> List[ProductResult]:
        """Search IKEA website for products."""
        if self.test_mode:
            logger.info("Using test mode - returning dynamic dummy results")
            return self._generate_dummy_results(query, max_results)
            
        try:
            # Implement rate limiting
            self._rate_limit()
            
            # Construct the search URL with proper encoding
            encoded_query = quote_plus(query)
            search_url = f"{self.SEARCH_URL}{encoded_query}"
            logger.debug(f"Searching IKEA: {search_url}")
            
            # Make the request
            response = requests.get(search_url, headers=self.headers, timeout=10)
            logger.debug(f"IKEA Response Status: {response.status_code}")
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find product items using updated selectors
            product_items = soup.select('.pip-product-compact, .pip-product-pip')
            logger.debug(f"Found {len(product_items)} product items")
            
            results = []
            for item in product_items[:max_results]:
                try:
                    # Extract product information using updated selectors
                    title_elem = item.select_one('.pip-header-section__title, .pip-product-pip__title')
                    link_elem = item.select_one('a[href*="/p/"]')
                    desc_elem = item.select_one('.pip-product-compact__rating-text, .pip-product-pip__description')
                    
                    if title_elem and link_elem:
                        title = title_elem.text.strip()
                        link = link_elem.get('href', '')
                        if not link.startswith('http'):
                            link = f"{self.BASE_URL}{link}"
                        
                        # Create snippet with description if available
                        snippet = "IKEA product"
                        if desc_elem:
                            snippet = desc_elem.text.strip()
                        
                        # Try to extract model number from the link
                        model = None
                        if '/p/' in link:
                            model = link.split('/p/')[-1].split('/')[0]
                        
                        result = ProductResult(
                            title=title,
                            snippet=snippet,
                            source='ikea',
                            links=[link],
                            model=model
                        )
                        
                        # Only add if not a duplicate
                        if not self.is_duplicate(result, results):
                            results.append(result)
                            logger.debug(f"Added result: {title}")
                            
                except Exception as e:
                    logger.error(f"Error parsing IKEA product: {e}", exc_info=True)
                    continue
            
            logger.info(f"Returning {len(results)} IKEA results")
            return results
            
        except requests.exceptions.Timeout:
            logger.error("Timeout while searching IKEA")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while searching IKEA: {e}")
            return []
        except Exception as e:
            logger.error(f"Error in IKEA scraper: {e}", exc_info=True)
            return [] 