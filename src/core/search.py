import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
from pathlib import Path

logger = logging.getLogger(__name__)

class SearchEngine:
    """Search engine for finding and indexing manual content."""
    
    def __init__(self):
        self.manual_sources = [
            "manualslib.com",
            "manuals.plus",
            "manualowl.com",
            "support.hp.com",
            "support.samsung.com",
            "support.apple.com",
            "support.microsoft.com"
        ]
        self.session = None
    
    async def _get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    def _is_valid_manual_url(self, url: str) -> bool:
        """Check if URL is from a trusted manual source."""
        parsed = urlparse(url)
        return any(source in parsed.netloc for source in self.manual_sources)

    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content."""
        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def _extract_manual_content(self, html: str, url: str) -> Dict:
        """Extract relevant content from manual page."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer']):
            element.decompose()

        # Extract title
        title = soup.find('title')
        title = title.text.strip() if title else "Untitled Manual"

        # Extract main content
        content = ""
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article'))
        if main_content:
            content = main_content.get_text(separator=' ', strip=True)
        else:
            content = soup.get_text(separator=' ', strip=True)

        # Extract source
        source = urlparse(url).netloc

        return {
            "title": title,
            "content": content,
            "url": url,
            "source": source,
            "date": datetime.now().strftime("%Y-%m-%d")
        }

    async def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for manuals across trusted sources."""
        # For now, return some sample results
        return [
            {
                "title": "Sample Manual 1",
                "snippet": "This is a sample manual about " + query,
                "url": "https://example.com/manual1",
                "source": "example.com",
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "Sample Manual 2",
                "snippet": "Another sample manual related to " + query,
                "url": "https://example.com/manual2",
                "source": "example.com",
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        ]

    async def crawl_and_index(self, url: str) -> bool:
        """Crawl and index a specific manual URL."""
        try:
            if not self._is_valid_manual_url(url):
                return False

            html = await self._fetch_page(url)
            if not html:
                return False

            content = self._extract_manual_content(html, url)
            return bool(content["content"])
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