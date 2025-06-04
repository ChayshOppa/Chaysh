import os
import logging
from typing import Dict, List, Optional
import openai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class Assistant:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.warning("OpenAI API key not found in environment variables")

    def generate_response(self, query: str, context: Dict) -> Dict:
        """
        Generate AI response based on user query and manual context.
        """
        try:
            if not self.api_key:
                return {
                    'error': 'OpenAI API key not configured',
                    'response': 'Please configure OpenAI API key to use AI features.'
                }

            # Prepare the prompt with context
            prompt = self._prepare_prompt(query, context)
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that explains product manuals and guides."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            
            return {
                'response': response.choices[0].message.content,
                'steps': self._extract_steps(response.choices[0].message.content)
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return {
                'error': str(e),
                'response': 'Sorry, I encountered an error while processing your request.'
            }

    def _prepare_prompt(self, query: str, context: Dict) -> str:
        """
        Prepare the prompt for the AI model.
        """
        return f"""
        Based on the following manual content, please help with this query: {query}
        
        Manual Title: {context.get('title', '')}
        Content: {context.get('content', '')}
        
        Please provide a clear, step-by-step response.
        """

    def _extract_steps(self, response: str) -> List[str]:
        """
        Extract steps from AI response.
        """
        steps = []
        for line in response.split('\n'):
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', 'Step', 'step')):
                steps.append(line.strip())
        return steps 