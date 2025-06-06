import logging
import httpx
from typing import Dict, List, Optional
from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class Assistant:
    """AI Assistant for manual content."""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        if not self.api_key:
            logger.warning("OpenRouter API key not found in environment variables")
        else:
            logger.info("OpenRouter API key loaded in Assistant")
        self.api_url = settings.OPENROUTER_API_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self.client.aclose()
    
    async def generate_response(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Generate response for manual content using OpenRouter API.
        
        Args:
            query: User's question or request
            context: Optional context from search results
            
        Returns:
            Dict containing response and any extracted steps
        """
        try:
            if not self.api_key:
                logger.error("OpenRouter API key not configured")
                return {
                    'error': 'OpenRouter API key not configured',
                    'response': 'Please configure OpenRouter API key to use AI features.'
                }

            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://chaysh.com",
                "X-Title": "Chaysh Manual Search"
            }
            
            payload = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that provides accurate and concise information about products and manuals."},
                    {"role": "user", "content": query}
                ]
            }

            # Log request details
            logger.info(f"Sending request to OpenRouter API: {self.api_url}")
            logger.info(f"Request headers: {headers}")
            logger.info(f"Request payload: {payload}")

            # Make request
            response = await self.client.post(self.api_url, json=payload, headers=headers)
            
            # Log response
            logger.info(f"OpenRouter API response status: {response.status_code}")
            logger.info(f"OpenRouter API response: {response.text}")

            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    message = data["choices"][0]["message"]["content"]
                    logger.info(f"AI response: {message}")
                    return {
                        'response': message,
                        'steps': self._extract_steps(message)
                    }
                else:
                    logger.error("Invalid response format from OpenRouter API")
                    return {
                        'error': 'Invalid response format from API',
                        'response': 'Sorry, I encountered an error while processing your request.'
                    }
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return {
                    'error': f'API error: {response.status_code}',
                    'response': 'Sorry, I encountered an error while processing your request.'
                }

        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {str(e)}", exc_info=True)
            return {
                'error': str(e),
                'response': 'Sorry, I encountered an error while processing your request.'
            }
    
    def _extract_steps(self, text: str) -> List[str]:
        """Extract steps from AI response text."""
        # Simple step extraction - split by numbered lines
        steps = []
        for line in text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('- ')):
                steps.append(line)
        return steps 