import httpx
import logging
from typing import Dict, List, Optional
from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class Assistant:
    """AI Assistant using OpenRouter API."""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.MODEL_NAME
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://chaysh.com",  # Replace with your domain
            "X-Title": "Chaysh Assistant"
        }
    
    async def generate_response(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Generate AI response using OpenRouter API.
        
        Args:
            query: User's question or request
            context: Optional context from search results
            
        Returns:
            Dict containing response and any extracted steps
        """
        try:
            # Prepare the prompt
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that explains product manuals and guides. "
                              "Provide clear, step-by-step instructions when possible."
                }
            ]
            
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Context from manual: {context.get('content', '')}"
                })
            
            messages.append({
                "role": "user",
                "content": query
            })
            
            # Call OpenRouter API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": 500
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # Extract the response
                ai_response = result["choices"][0]["message"]["content"]
                
                return {
                    "response": ai_response,
                    "steps": self._extract_steps(ai_response)
                }
                
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return {
                "error": str(e),
                "response": "Sorry, I encountered an error while processing your request."
            }
    
    def _extract_steps(self, response: str) -> List[str]:
        """Extract step-by-step instructions from the response."""
        steps = []
        for line in response.split('\n'):
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', 'Step', 'step')):
                steps.append(line.strip())
        return steps 