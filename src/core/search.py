import httpx
import logging
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class SearchEngine:
    """Search engine for finding and indexing manual content."""
    
    def __init__(self):
        self.schema = Schema(
            title=TEXT(stored=True),
            content=TEXT(stored=True),
            url=ID(stored=True),
            source=TEXT(stored=True)
        )
        
        # Create index directory if it doesn't exist
        self.index_dir = Path("data/index")
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Create or open the index
        self.ix = create_in(str(self.index_dir), self.schema)
        self.writer = self.ix.writer()
    
    async def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for manual content.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            with self.ix.searcher() as searcher:
                query_parser = QueryParser("content", self.schema)
                q = query_parser.parse(query)
                results = searcher.search(q, limit=limit)
                
                return [
                    {
                        "title": result["title"],
                        "content": result["content"],
                        "url": result["url"],
                        "source": result["source"]
                    }
                    for result in results
                ]
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            return []
    
    async def crawl_and_index(self, url: str) -> bool:
        """
        Crawl a URL and index its content.
        
        Args:
            url: URL to crawl
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "lxml")
                
                # Extract title and content
                title = soup.title.string if soup.title else url
                content = soup.get_text(separator=" ", strip=True)
                
                # Add to index
                self.writer.add_document(
                    title=title,
                    content=content,
                    url=url,
                    source="web"
                )
                self.writer.commit()
                
                return True
                
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return False
    
    def is_manual_page(self, url: str, content: str) -> bool:
        """
        Determine if the page is likely a manual or guide.
        """
        manual_keywords = [
            "manual", "guide", "instructions", "tutorial",
            "how to", "documentation", "help", "support"
        ]
        return any(keyword in url.lower() or keyword in content.lower() 
                  for keyword in manual_keywords) 