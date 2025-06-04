from scrapers.unified_scraper import UnifiedScraper, IkeaScraper, ManualslibScraper
import logging
import sys
import json
from datetime import datetime

# Configure logging to show both in console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scraper_test.log')
    ]
)
logger = logging.getLogger(__name__)

def save_test_results(results: dict, filename: str = 'test_results.json'):
    """Save test results to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

def test_individual_scrapers():
    """Test each scraper individually"""
    scrapers = {
        'IKEA': IkeaScraper(),
        'Manualslib': ManualslibScraper()
    }
    
    test_queries = [
        "billy",  # IKEA bookcase
        "canon",  # Camera manuals
        "malm",   # IKEA furniture
        "sony",   # Electronics manuals
        "canon printer"  # Printer manuals
    ]
    
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'scrapers': {}
    }
    
    for scraper_name, scraper in scrapers.items():
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing {scraper_name} scraper")
        logger.info(f"{'='*50}")
        
        scraper_results = {
            'queries': {},
            'status': scraper.status.to_dict()
        }
        
        for query in test_queries:
            logger.info(f"\nTesting query: {query}")
            query_results = {
                'results': [],
                'error': None
            }
            
            try:
                results = scraper.search(query)
                logger.info(f"Found {len(results)} results")
                
                for i, result in enumerate(results, 1):
                    logger.info(f"\nResult {i}:")
                    logger.info(f"Title: {result['title']}")
                    logger.info(f"Link: {result['link']}")
                    if result['snippet']:
                        logger.info(f"Snippet: {result['snippet']}")
                    logger.info("-" * 50)
                    
                    query_results['results'].append(result)
                    
            except Exception as e:
                error_msg = f"Error testing {scraper_name} with query '{query}': {str(e)}"
                logger.error(error_msg)
                query_results['error'] = error_msg
            
            scraper_results['queries'][query] = query_results
        
        test_results['scrapers'][scraper_name] = scraper_results
    
    return test_results

def test_unified_scraper():
    """Test the unified scraper"""
    logger.info(f"\n{'='*50}")
    logger.info("Testing Unified Scraper")
    logger.info(f"{'='*50}")
    
    scraper = UnifiedScraper()
    test_queries = [
        "billy",  # IKEA bookcase
        "canon",  # Camera manuals
        "malm",   # IKEA furniture
        "sony",   # Electronics manuals
        "canon printer"  # Printer manuals
    ]
    
    unified_results = {
        'timestamp': datetime.now().isoformat(),
        'queries': {},
        'status': scraper.get_status()
    }
    
    for query in test_queries:
        logger.info(f"\nTesting unified search for: {query}")
        query_results = {
            'results': [],
            'error': None
        }
        
        try:
            results = scraper.search(query)
            logger.info(f"Found {len(results)} total results")
            
            for i, result in enumerate(results, 1):
                logger.info(f"\nResult {i}:")
                logger.info(f"Title: {result['title']}")
                logger.info(f"Source: {result['source']}")
                logger.info(f"Link: {result['link']}")
                if result['snippet']:
                    logger.info(f"Snippet: {result['snippet']}")
                logger.info("-" * 50)
                
                query_results['results'].append(result)
                
        except Exception as e:
            error_msg = f"Error testing unified search with query '{query}': {str(e)}"
            logger.error(error_msg)
            query_results['error'] = error_msg
        
        unified_results['queries'][query] = query_results
    
    return unified_results

if __name__ == "__main__":
    logger.info("Starting scraper tests...")
    
    # Test individual scrapers
    individual_results = test_individual_scrapers()
    save_test_results(individual_results, 'individual_test_results.json')
    
    # Test unified scraper
    unified_results = test_unified_scraper()
    save_test_results(unified_results, 'unified_test_results.json')
    
    logger.info("Scraper tests completed. Check scraper_test.log for detailed results.")
    logger.info("Test results saved to individual_test_results.json and unified_test_results.json") 