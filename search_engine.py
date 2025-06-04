from typing import List, Dict
from dataclasses import dataclass
from scrapers.ikea_scraper import IkeaScraper
from scrapers.manualslib_scraper import ManualslibScraper
import logging
import random

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Class to hold search results and statistics."""
    results: List[Dict]
    stats: Dict[str, int]

class SearchEngine:
    """Search engine that combines results from multiple sources."""
    
    def __init__(self, test_mode=False):
        """Initialize search engine with scrapers."""
        self.ikea_scraper = IkeaScraper(test_mode=test_mode)
        self.manualslib_scraper = ManualslibScraper(test_mode=test_mode)
    
    def search(self, query: str, max_results: int = 10) -> SearchResult:
        """Search across all sources and combine results."""
        logger.info(f"Searching for: {query}")
        
        # Get up to 10 results from each source
        ikea_results = self.ikea_scraper.search(query, max_results)
        manualslib_results = self.manualslib_scraper.search(query, max_results)
        
        # Log number of results from each source
        logger.info(f"Found {len(ikea_results)} results from IKEA")
        logger.info(f"Found {len(manualslib_results)} results from ManualLib")
        
        # Combine and shuffle results
        all_results = []
        for result in ikea_results:
            all_results.append({
                'title': result.title,
                'snippet': result.snippet,
                'model': result.model,
                'ikea_link': result.links[0] if result.links else None,
                'manualslib_link': None
            })
        for result in manualslib_results:
            all_results.append({
                'title': result.title,
                'snippet': result.snippet,
                'model': result.model,
                'ikea_link': None,
                'manualslib_link': result.links[0] if result.links else None
            })
        random.shuffle(all_results)
        combined_results = all_results[:max_results]
        
        # Prepare response with statistics
        response = SearchResult(
            results=combined_results,
            stats={
                'total_results': len(combined_results),
                'ikea_results': len(ikea_results),
                'manualslib_results': len(manualslib_results),
                'combined_results': sum(1 for r in combined_results if r['ikea_link'] and r['manualslib_link'])
            }
        )
        
        logger.info(f"Total combined results: {response.stats['total_results']}")
        return response 