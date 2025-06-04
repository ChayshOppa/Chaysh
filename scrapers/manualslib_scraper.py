import requests
from bs4 import BeautifulSoup
from typing import List
from scrapers.base_scraper import BaseScraper, ProductResult
import logging
import time
from urllib.parse import quote_plus
import random

logger = logging.getLogger(__name__)

class ManualslibScraper(BaseScraper):
    """Scraper for Manualslib website to find product manuals."""
    
    BASE_URL = "https://www.manualslib.com"
    
    # Common product brands and their manuals
    PRODUCT_BRANDS = {
        'canon': {
            'name': 'Canon',
            'type': 'camera',
            'models': [
                {
                    'name': 'EOS R5',
                    'model': 'EOS R5',
                    'manuals': [
                        {'type': 'User Manual', 'desc': 'Complete user manual with setup and operation instructions'},
                        {'type': 'Quick Start Guide', 'desc': 'Basic setup and essential functions'},
                        {'type': 'Troubleshooting Guide', 'desc': 'Common issues and solutions'}
                    ]
                },
                {
                    'name': 'EOS R6',
                    'model': 'EOS R6',
                    'manuals': [
                        {'type': 'User Manual', 'desc': 'Complete user manual with setup and operation instructions'},
                        {'type': 'Quick Start Guide', 'desc': 'Basic setup and essential functions'},
                        {'type': 'Troubleshooting Guide', 'desc': 'Common issues and solutions'}
                    ]
                }
            ]
        },
        'samsung': {
            'name': 'Samsung',
            'type': 'phone',
            'models': [
                {
                    'name': 'Galaxy S21',
                    'model': 'SM-G991B',
                    'manuals': [
                        {'type': 'User Manual', 'desc': 'Complete user manual with all features and settings'},
                        {'type': 'Quick Start Guide', 'desc': 'Basic setup and essential features'},
                        {'type': 'Safety Guide', 'desc': 'Safety and warranty information'}
                    ]
                },
                {
                    'name': 'Galaxy S22',
                    'model': 'SM-S901B',
                    'manuals': [
                        {'type': 'User Manual', 'desc': 'Complete user manual with all features and settings'},
                        {'type': 'Quick Start Guide', 'desc': 'Basic setup and essential features'},
                        {'type': 'Safety Guide', 'desc': 'Safety and warranty information'}
                    ]
                }
            ]
        },
        'sony': {
            'name': 'Sony',
            'type': 'headphones',
            'models': [
                {
                    'name': 'WH-1000XM4',
                    'model': 'WH-1000XM4',
                    'manuals': [
                        {'type': 'User Manual', 'desc': 'Complete user manual with all features and settings'},
                        {'type': 'Quick Start Guide', 'desc': 'Basic setup and essential functions'},
                        {'type': 'Troubleshooting Guide', 'desc': 'Common issues and solutions'}
                    ]
                },
                {
                    'name': 'WH-1000XM5',
                    'model': 'WH-1000XM5',
                    'manuals': [
                        {'type': 'User Manual', 'desc': 'Complete user manual with all features and settings'},
                        {'type': 'Quick Start Guide', 'desc': 'Basic setup and essential functions'},
                        {'type': 'Troubleshooting Guide', 'desc': 'Common issues and solutions'}
                    ]
                }
            ]
        }
    }
    
    DUMMY_EXTRA_FIELDS = [
        'Pages', 'Language', 'File Size', 'Format', 'Release Year', 'Author', 'Publisher',
        'Country', 'Manual Type', 'Downloadable'
    ]
    DUMMY_LANGUAGES = ['English', 'Polish', 'German', 'French', 'Spanish']
    DUMMY_FORMATS = ['PDF', 'HTML', 'EPUB']
    DUMMY_AUTHORS = ['IKEA', 'Canon Inc.', 'Samsung Electronics', 'Sony Corporation', 'Manualslib']
    DUMMY_PUBLISHERS = ['Manualslib', 'Official', 'User Community']
    DUMMY_COUNTRIES = ['Poland', 'Sweden', 'Germany', 'China', 'Japan']
    
    def __init__(self, test_mode=False):
        super().__init__()
        self.test_mode = test_mode
        self.last_request_time = 0
        self.min_request_interval = 2
        self.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
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
        all_manuals = []
        # Gather all possible manuals
        for brand_key, brand_info in self.PRODUCT_BRANDS.items():
            for model_info in brand_info['models']:
                for manual in model_info['manuals']:
                    all_manuals.append((brand_info, model_info, manual))
        # If query matches a brand, bias results toward that
        matching_manuals = []
        for brand_key, brand_info in self.PRODUCT_BRANDS.items():
            if brand_key in query_lower or brand_info['name'].lower() in query_lower:
                for model_info in brand_info['models']:
                    for manual in model_info['manuals']:
                        matching_manuals.append((brand_info, model_info, manual))
        # Use matching or random manuals
        chosen = matching_manuals if matching_manuals else all_manuals
        chosen = random.sample(chosen, min(max_results, len(chosen)))
        for brand_info, model_info, manual in chosen:
            # Generate 10 info fields
            info = {
                'Pages': random.randint(10, 300),
                'Language': random.choice(self.DUMMY_LANGUAGES),
                'File Size': f"{random.randint(1, 20)} MB",
                'Format': random.choice(self.DUMMY_FORMATS),
                'Release Year': random.randint(2015, 2024),
                'Author': random.choice(self.DUMMY_AUTHORS),
                'Publisher': random.choice(self.DUMMY_PUBLISHERS),
                'Country': random.choice(self.DUMMY_COUNTRIES),
                'Manual Type': manual['type'],
                'Downloadable': random.choice(['Yes', 'No'])
            }
            title = f"{brand_info['name']} {model_info['name']} {manual['type']}"
            link = f"{self.BASE_URL}/{brand_info['name'][0]}/{brand_info['name']}-{model_info['name']}-{manual['type'].replace(' ', '-')}.html"
            snippet = f"{manual['desc']} | Pages: {info['Pages']}, Language: {info['Language']}, Size: {info['File Size']}"
            # Add all info fields to snippet for display
            full_snippet = snippet + \
                f" | Format: {info['Format']}, Year: {info['Release Year']}, Author: {info['Author']}, " \
                f"Publisher: {info['Publisher']}, Country: {info['Country']}, Downloadable: {info['Downloadable']}"
            result = ProductResult(
                title=title,
                snippet=full_snippet,
                source='manualslib',
                links=[link],
                model=model_info['model']
            )
            results.append(result)
        return results
    
    def search(self, query: str, max_results: int = 10) -> List[ProductResult]:
        """Search Manualslib website for manuals."""
        if self.test_mode:
            logger.info("Using test mode - returning dynamic dummy results")
            return self._generate_dummy_results(query, max_results)
            
        try:
            # Implement rate limiting
            self._rate_limit()
            
            # Construct the search URL following the rules
            first_letter = query[0].upper()
            encoded_query = quote_plus(query)
            search_url = f"{self.BASE_URL}/{first_letter}/{encoded_query}.html"
            logger.debug(f"Searching Manualslib: {search_url}")
            
            # Make the request
            response = requests.get(search_url, headers=self.headers, timeout=10)
            logger.debug(f"Manualslib Response Status: {response.status_code}")
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find manual items using updated selectors
            manual_items = soup.select('.mdl-left h3 a, .mdl-right h3 a')
            logger.debug(f"Found {len(manual_items)} manual items")
            
            results = []
            for item in manual_items[:max_results]:
                try:
                    title = item.text.strip()
                    link = item.get('href', '')
                    if not link.startswith('http'):
                        link = f"{self.BASE_URL}{link}"
                    
                    # Try to get description from sibling div or parent
                    desc_elem = item.find_next_sibling('div') or item.parent.find_next_sibling('div')
                    snippet = "Manual available"
                    if desc_elem:
                        snippet = desc_elem.text.strip()
                    
                    # Try to extract model number from the title or link
                    model = None
                    if 'model' in title.lower():
                        model = title.split('model')[-1].strip().split()[0]
                    elif 'manual' in title.lower():
                        # Try to extract model from the title
                        parts = title.split('-')
                        if len(parts) > 1:
                            model = parts[1].strip()
                    
                    result = ProductResult(
                        title=title,
                        snippet=snippet,
                        source='manualslib',
                        links=[link],
                        model=model
                    )
                    
                    # Only add if not a duplicate
                    if not self.is_duplicate(result, results):
                        results.append(result)
                        logger.debug(f"Added result: {title}")
                        
                except Exception as e:
                    logger.error(f"Error parsing Manualslib item: {e}", exc_info=True)
                    continue
            
            logger.info(f"Returning {len(results)} Manualslib results")
            return results
            
        except requests.exceptions.Timeout:
            logger.error("Timeout while searching Manualslib")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while searching Manualslib: {e}")
            return []
        except Exception as e:
            logger.error(f"Error in Manualslib scraper: {e}", exc_info=True)
            return [] 