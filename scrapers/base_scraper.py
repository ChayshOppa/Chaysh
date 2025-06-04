from dataclasses import dataclass
from typing import List, Optional
from abc import ABC, abstractmethod

@dataclass
class ProductResult:
    """Represents a product search result."""
    title: str
    snippet: str
    source: str
    links: List[str]
    model: Optional[str] = None

class BaseScraper(ABC):
    """Base class for all scrapers."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    @abstractmethod
    def search(self, query: str, max_results: int = 10) -> List[ProductResult]:
        """Base search method to be implemented by child classes."""
        pass
    
    def normalize_title(self, title: str) -> str:
        """Normalize product titles for better matching."""
        return title.lower().strip()
    
    def is_duplicate(self, result: ProductResult, existing_results: List[ProductResult]) -> bool:
        """Check if a result is a duplicate based on title."""
        return any(r.title.lower() == result.title.lower() for r in existing_results) 