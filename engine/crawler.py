import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class Crawler:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def crawl(self, url: str) -> Optional[Dict]:
        """
        Crawl a given URL and extract manual-related content.
        Returns a dictionary with title, content, and metadata.
        """
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract title
            title = soup.title.string if soup.title else url
            
            # Extract content (basic implementation)
            content = soup.get_text(separator=' ', strip=True)
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'source': 'web'
            }
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return None

    def is_manual_page(self, url: str, content: str) -> bool:
        """
        Determine if the page is likely a manual or guide.
        """
        manual_keywords = ['manual', 'guide', 'instructions', 'tutorial', 'how to']
        return any(keyword in url.lower() or keyword in content.lower() 
                  for keyword in manual_keywords) 