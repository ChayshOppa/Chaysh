import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
import json
import random
import collections
import os
import httpx
from .select_model import ModelSelector

class ManualCrawler:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.top_results = 5
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        if not self.OPENROUTER_API_KEY:
            logging.error("OpenRouter API key not found in environment variables")
        self.OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
        self.search_engines = [
            "https://www.google.com/search?q=",
            "https://www.bing.com/search?q=",
            "https://search.yahoo.com/search?p="
        ]
        self.ai_client = None
        self.model_selector = None

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
        if not self.ai_client:
            self.ai_client = httpx.AsyncClient(headers=self.headers)
        if not self.model_selector:
            self.model_selector = ModelSelector(self.ai_client)

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None
        if self.ai_client:
            await self.ai_client.aclose()
            self.ai_client = None
        self.model_selector = None

    async def ask_ai(self, prompt: str, language: str = 'en') -> str:
        """Ask the AI model a question using OpenRouter API."""
        try:
            # Get API key from environment
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                logging.error("OpenRouter API key not found in environment variables")
                return ""

            # Language-specific instructions and box titles
            lang_config = {
                'en': {
                    'instruction': "Answer in English.",
                    'boxes': {
                        'current_model': 'Current Model',
                        'select_model': 'Select Model',
                        'opinions': 'User Opinions',
                        'manuals': 'Manuals & Tutorials'
                    }
                },
                'pl': {
                    'instruction': "Odpowiadaj wyłącznie po polsku.",
                    'boxes': {
                        'current_model': 'Aktualny Model',
                        'select_model': 'Wybierz Model',
                        'opinions': 'Opinie Użytkowników',
                        'manuals': 'Instrukcje i Poradniki'
                    }
                }
            }
            
            config = lang_config.get(language, lang_config['en'])
            
            # Create structured prompt
            structured_prompt = f"""
            {config['instruction']}
            
            Analyze the following query: "{prompt}"
            
            Please provide information in this exact format:
            {{
                "basic_info": "A brief overview (max 100 chars)",
                "detailed_info": "What is this item? What information can be found about it? (max 150 chars)",
                "product_info": "If it's a product, include pricing and opinions (max 150 chars)",
                "summary": "A concise explanation of what we know about this item (max 300 chars total)",
                "opinions": [
                    {{
                        "text": "A user opinion or review (max 100 chars)",
                        "rating": "positive/negative/neutral"
                    }}
                ],
                "manuals": [
                    {{
                        "title": "Manual or tutorial title",
                        "type": "manual/tutorial/guide",
                        "url": "placeholder_url"
                    }}
                ]
            }}

            Rules:
            1. Keep all responses under the specified character limits
            2. Focus on factual, verifiable information
            3. If it's a product, include pricing and user opinions
            4. Make the summary clear and easy to understand
            5. Return ONLY valid JSON format
            6. {config['instruction']}
            """

            # Prepare request
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://chaysh.com",
                "X-Title": "Chaysh Manual Search"
            }
            
            payload = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": f"You are a helpful assistant that provides accurate and concise information. Always respond in valid JSON format. {config['instruction']}"},
                    {"role": "user", "content": structured_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }

            # Log request details
            logging.info(f"Sending request to OpenRouter API: {url}")
            logging.info(f"Request headers: {headers}")
            logging.info(f"Request payload: {payload}")

            # Make request
            response = await self.ai_client.post(url, json=payload, headers=headers)
                
            # Log response
            logging.info(f"OpenRouter API response status: {response.status_code}")
            logging.info(f"OpenRouter API response: {response.text}")

            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    message = data["choices"][0]["message"]["content"]
                    logging.info(f"AI response: {message}")
                    return message
                else:
                    logging.error(f"Invalid response format from OpenRouter API: {data}")
                    return ""
            else:
                logging.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return ""

        except Exception as e:
            logging.error(f"Error calling OpenRouter API: {str(e)}", exc_info=True)
            return ""

    def is_relevant_title(self, title: str, query: str, relaxed=False) -> bool:
        title_lower = title.lower()
        query_lower = query.lower()
        # Ignore forums, ads, spam, and unrelated content
        if any(x in title_lower for x in ["forum", "discussion", "community", "review", "ad", "sponsored"]):
            return False
        # Prioritize titles containing the query or product/brand keywords
        if relaxed:
            return any(word in title_lower for word in query_lower.split())
        return query_lower in title_lower or any(word in title_lower for word in query_lower.split())

    async def search_manuals(self, query: str, context: Optional[list] = None, language: str = 'en') -> List[Dict]:
        await self.init_session()
        try:
            context_text = ""
            if context and len(context) > 0:
                context_text = f"User's recent queries: {context}\n"

            # Language-specific configurations
            lang_config = {
                'en': {
                    'suggestions': [
                        {"text": f"Having trouble with '{query}'? Some help would be needed.", "category": "help"},
                        {"text": f"Wondering what exactly '{query}' is?", "category": "manual"},
                        {"text": f"Not sure what is exact name of '{query}'?", "category": "model_search"},
                        {"text": f"Let's see what others think about '{query}'.", "category": "opinions"}
                    ],
                    'boxes': {
                        'current_model': 'Current Model',
                        'select_model': 'Select Model',
                        'opinions': 'User Opinions',
                        'manuals': 'Manuals & Tutorials'
                    }
                },
                'pl': {
                    'suggestions': [
                        {"text": f"Masz problem z '{query}'? Potrzebna pomoc.", "category": "help"},
                        {"text": f"Zastanawiasz się czym dokładnie jest '{query}'?", "category": "manual"},
                        {"text": f"Nie jesteś pewien dokładnej nazwy '{query}'?", "category": "model_search"},
                        {"text": f"Zobaczmy co inni myślą o '{query}'.", "category": "opinions"}
                    ],
                    'boxes': {
                        'current_model': 'Aktualny Model',
                        'select_model': 'Wybierz Model',
                        'opinions': 'Opinie Użytkowników',
                        'manuals': 'Instrukcje i Poradniki'
                    }
                }
            }
            
            config = lang_config.get(language, lang_config['en'])
            static_suggestions = config['suggestions']

            # Get AI response with language parameter
            answer_response = await self.ask_ai(query, language)
            try:
                answer = self.extract_first_json(answer_response)
                if not answer:
                    raise ValueError("Failed to extract JSON from AI response")
                
                # Get model variations
                variations_data = await self.model_selector.get_model_variations(query)
                
                # Initialize action boxes
                action_boxes = []
                
                # Box 1: Model Variations
                if variations_data.get('is_specific'):
                    action_boxes.append({
                        'title': config['boxes']['current_model'],
                        'type': 'info',
                        'message': 'You are viewing a specific model' if language == 'en' else 'Przeglądasz konkretny model'
                    })
                else:
                    # Convert variations into clickable actions
                    variation_actions = []
                    for variation in variations_data.get('variations', []):
                        variation_actions.append({
                            'type': 'search',
                            'label': variation['name'],
                            'query': variation['query']
                        })
                    
                    action_boxes.append({
                        'title': config['boxes']['select_model'],
                        'type': 'variations',
                        'variations': variations_data.get('variations', []),
                        'actions': variation_actions
                    })
                
                # Box 2: Opinions
                opinions = answer.get('opinions', [])
                if opinions:
                    action_boxes.append({
                        'title': config['boxes']['opinions'],
                        'type': 'opinions',
                        'opinions': opinions
                    })
                else:
                    action_boxes.append({
                        'title': config['boxes']['opinions'],
                        'type': 'placeholder',
                        'message': 'No opinions available yet' if language == 'en' else 'Brak dostępnych opinii'
                    })
                
                # Box 3: Manuals/Tutorials
                manuals = answer.get('manuals', [])
                if manuals:
                    action_boxes.append({
                        'title': config['boxes']['manuals'],
                        'type': 'manuals',
                        'manuals': manuals
                    })
                else:
                    action_boxes.append({
                        'title': config['boxes']['manuals'],
                        'type': 'placeholder',
                        'message': 'No manuals available yet' if language == 'en' else 'Brak dostępnych instrukcji'
                    })
                
                # Format the response according to our structure
                formatted_response = {
                    'name': query,
                    'description': [
                        answer.get('basic_info', ''),
                        answer.get('detailed_info', ''),
                        answer.get('product_info', '')
                    ],
                    'source_info': 'AI-generated information based on available data' if language == 'en' else 'Informacje wygenerowane przez AI na podstawie dostępnych danych',
                    'action_boxes': action_boxes,
                    'suggestions': static_suggestions,
                    'actions': [{'type': 'chat', 'label': 'Chaysh Assistant', 'query': query}]
                }
                
                # Clean up empty descriptions
                formatted_response['description'] = [d for d in formatted_response['description'] if d]
                
                # Add summary if available
                if 'summary' in answer and answer['summary']:
                    formatted_response['description'].append(answer['summary'])
                
                logging.info(f"Formatted AI response: {formatted_response}")
                return [formatted_response]
                
            except Exception as e:
                logging.error(f"Error processing AI response: {str(e)}", exc_info=True)
                return [{
                    'name': query,
                    'description': ['Unable to process the search request. Please try again.'] if language == 'en' else ['Nie można przetworzyć zapytania. Spróbuj ponownie.'],
                    'source_info': 'Error processing request' if language == 'en' else 'Błąd przetwarzania zapytania',
                    'action_boxes': [],
                    'suggestions': static_suggestions,
                    'actions': [{'type': 'chat', 'label': 'Chaysh Assistant', 'query': query}]
                }]
                
        except Exception as e:
            logging.error(f"Error in search_manuals: {str(e)}", exc_info=True)
            return [{
                'name': query,
                'description': ['An error occurred while processing your search.'] if language == 'en' else ['Wystąpił błąd podczas przetwarzania wyszukiwania.'],
                'source_info': 'Error processing request' if language == 'en' else 'Błąd przetwarzania zapytania',
                'action_boxes': [],
                'suggestions': [],
                'actions': [{'type': 'chat', 'label': 'Chaysh Assistant', 'query': query}]
            }]
        finally:
            await self.close_session()

    async def analyze_search_intent(self, query: str) -> Dict:
        """Use AI to understand what the user is looking for."""
        prompt = f"""
        Analyze this search query and provide:
        1. Main product being searched
        2. Brand (if mentioned)
        3. Specific model (if mentioned)
        4. Type of information needed (manual, specs, reviews)
        
        Query: {query}
        
        Respond in JSON format:
        {{
            "product": "string",
            "brand": "string",
            "model": "string",
            "info_type": "string"
        }}
        """
        
        response = await self.ask_ai(prompt)
        logging.info(f"Raw AI response: {response}")
        print("\n===== RAW AI RESPONSE =====\n", response, "\n==========================\n")
        try:
            return json.loads(response)
        except:
            return {
                "product": query,
                "brand": "",
                "model": "",
                "info_type": "manual"
            }

    async def generate_search_queries(self, query: str, intent: Dict) -> List[str]:
        """Generate search queries for different search engines."""
        prompt = f"""
        Generate 5 different search queries to find information about:
        Product: {intent['product']}
        Brand: {intent['brand']}
        Model: {intent['model']}
        
        Include queries for:
        1. Product manuals
        2. Product specifications
        3. User reviews
        4. Price information
        
        Respond with a JSON array of strings.
        """
        
        response = await self.ask_ai(prompt)
        try:
            queries = json.loads(response)
            return queries
        except:
            return [query]

    def extract_search_links(self, html: str) -> List[str]:
        """Extract relevant links from search results."""
        soup = BeautifulSoup(html, 'lxml')
        links = []
        
        # Extract links from search results
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http') and not any(x in href for x in ['google.com', 'bing.com', 'yahoo.com']):
                links.append(href)
        
        return list(set(links))  # Remove duplicates

    async def analyze_page_content(self, html: str, query: str) -> Optional[Dict]:
        """Use AI to analyze page content and extract relevant information."""
        soup = BeautifulSoup(html, 'lxml')
        text = soup.get_text()[:2000]  # Limit text length for API
        
        prompt = f"""
        Analyze this webpage content and extract:
        1. Product description (max 100 chars)
        2. Rating (if available)
        3. Price (if available)
        
        Content: {text}
        
        Respond in JSON format:
        {{
            "description": "string",
            "rating": "string",
            "price": "string"
        }}
        """
        
        response = await self.ask_ai(prompt)
        try:
            info = json.loads(response)
            if info.get('description'):
                return info
        except:
            pass
        return None

    def extract_first_json(self, text: str) -> dict:
        """Extract the first valid JSON object from text."""
        try:
            # First try to parse the entire text as JSON
            return json.loads(text)
        except json.JSONDecodeError:
            try:
                # Look for JSON-like structure in the text
                import re
                json_pattern = r'\{[^{}]*\}'
                matches = re.findall(json_pattern, text)
                if matches:
                    for match in matches:
                        try:
                            return json.loads(match)
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logging.error(f"Error extracting JSON: {str(e)}")
            
            # If no valid JSON found, try to construct a basic response
            logging.warning(f"No valid JSON found in response: {text}")
            return {
                "name": "Unknown",
                "description": ["No valid description found in the response."],
                "source_info": "AI response parsing failed",
                "suggestions": [],
                "actions": []
            }

    async def aggregate_consensus(self, infos: List[Dict], query: str, top3: list, suggestions: list, all_titles: list) -> Optional[Dict]:
        """Use AI to generate a neutral consensus from 3 sources."""
        if not infos or len(infos) < 2:
            # Not enough info, fallback to basic info from titles/links
            descs = [i.get('description', '') for i in infos if i.get('description')]
            return {
                'name': query,
                'description': descs if descs else ["No detailed info found."],
                'source_info': f"Sources: {', '.join([t[1] for t in top3])}",
                'suggestions': suggestions,
                'actions': [
                    *[{'type': 'view', 'label': f'View Source {i+1}', 'url': t[1]} for i, t in enumerate(top3)],
                    {'type': 'chat', 'label': 'Chaysh Assistant', 'query': query}
                ]
            }
        prompt = f"""
        Given the following product information from 3 different sources, generate a single neutral summary with:
        1. Name/title
        2. Description (3 parts: short product/brand description, rating/quality, price/value)
        3. Small info about where the sources were collected from
        4. Up to 3 source links
        5. 5 suggestions for more specific searches (based on the most common words/models in the 30 titles)
        6. Here are the 30 page titles (each max 50 chars): {json.dumps(all_titles)}
        
        Infos: {json.dumps(infos, indent=2)}
        Query: {query}
        Suggestions: {json.dumps(suggestions)}
        
        Respond ONLY with a valid JSON object, no code block, no explanation, no markdown, no extra text:
        {{
            "name": "string",
            "description": ["short description", "rating/quality", "price/value"],
            "source_info": "string",
            "actions": [
                {{"type": "view", "label": "View Source 1", "url": "url1"}},
                {{"type": "view", "label": "View Source 2", "url": "url2"}},
                {{"type": "chat", "label": "Chaysh Assistant", "query": "{query}"}}
            ],
            "suggestions": ["string", ...]
        }}
        """
        try:
            response = await self.ask_ai(prompt)
            logging.info(f"Raw AI response: {response}")
            print("\n===== RAW AI RESPONSE =====\n", response, "\n==========================\n")
            consensus = self.extract_first_json(response)
            # Fallbacks for missing fields
            consensus['name'] = consensus.get('name', query)
            consensus['description'] = consensus.get('description', ["No description.", "", ""])
            consensus['source_info'] = consensus.get('source_info', f"Sources: {', '.join([t[1] for t in top3])}")
            consensus['suggestions'] = consensus.get('suggestions', suggestions)
            actions = []
            for i, t in enumerate(top3):
                actions.append({'type': 'view', 'label': f'View Source {i+1}', 'url': t[1]})
            actions.append({'type': 'chat', 'label': 'Chaysh Assistant', 'query': query})
            consensus['actions'] = actions
            return consensus
        except Exception as e:
            logging.error(f"Error in aggregate_consensus: {str(e)}")
            return None

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a webpage's content."""
        try:
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                logging.warning(f"Failed to fetch {url}: Status {response.status}")
                return None
        except Exception as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            return None

async def search_manuals(query: str, context: Optional[list] = None, language: str = 'en') -> List[Dict]:
    """Convenience function to search manuals"""
    crawler = ManualCrawler()
    return await crawler.search_manuals(query, context=context, language=language)

if __name__ == "__main__":
    asyncio.run(search_manuals("drill")) 