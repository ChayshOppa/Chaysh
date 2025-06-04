import re
from typing import Dict, List, Optional
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class Parser:
    def __init__(self):
        self.step_pattern = re.compile(r'(?:step|step\s+\d+)[:.]\s*(.*)', re.IGNORECASE)

    def parse_html(self, html_content: str) -> Dict:
        """
        Parse HTML content and extract structured information.
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Extract title
            title = soup.title.string if soup.title else ''
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            content = main_content.get_text(separator=' ', strip=True) if main_content else soup.get_text(separator=' ', strip=True)
            
            # Extract steps
            steps = self._extract_steps(content)
            
            return {
                'title': title,
                'content': content,
                'steps': steps
            }
            
        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
            return {'title': '', 'content': '', 'steps': []}

    def _extract_steps(self, content: str) -> List[str]:
        """
        Extract step-by-step instructions from content.
        """
        steps = []
        for line in content.split('\n'):
            match = self.step_pattern.search(line)
            if match:
                steps.append(match.group(1).strip())
        return steps 