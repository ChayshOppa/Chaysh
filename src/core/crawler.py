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

class ManualCrawler:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.top_results = 5
        self.OPENROUTER_API_KEY = "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"
        self.OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
        self.search_engines = [
            "https://www.google.com/search?q=",
            "https://www.bing.com/search?q=",
            "https://search.yahoo.com/search?p="
        ]

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def ask_ai(self, prompt: str) -> str:
        """Ask OpenRouter AI for help with understanding and processing."""
        headers = {
            "Authorization": f"Bearer {self.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yourusername/chaysh",
            "X-Title": "Chaysh"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that helps find and understand product information."},
                {"role": "user", "content": prompt}
            ]
        }
        
        logging.info(f"Sending request to OpenRouter API: {payload}")
        try:
            timeout = aiohttp.ClientTimeout(total=15)  # 15 seconds timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.OPENROUTER_API_URL, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        logging.info(f"OpenRouter API response: {data}")
                        return data["choices"][0]["message"]["content"].strip()
                    else:
                        logging.error(f"OpenRouter API error: {response.status}")
                        return ""
        except Exception as e:
            logging.error(f"Error calling OpenRouter API: {str(e)}")
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
            is_specific = any(char.isdigit() for char in query) or len(query.split()) > 1

            # Static suggestions with categories, English and Polish
            static_suggestions_en = [
                {"text": f"Not sure what is exact name of '{query}'?", "category": "model_search"},
                {"text": f"Wondering what exactly '{query}' is?", "category": "manual"},
                {"text": f"Having trouble with '{query}'? Some help would be needed.", "category": "help"},
                {"text": f"Let's see what others think about '{query}'.", "category": "opinions"},
            ]
            static_suggestions_pl = [
                {"text": f"Nie jesteś pewien dokładnej nazwy '{query}'?", "category": "model_search"},
                {"text": f"Zastanawiasz się czym dokładnie jest '{query}'?", "category": "manual"},
                {"text": f"Masz problem z '{query}'? Potrzebna pomoc.", "category": "help"},
                {"text": f"Zobaczmy co inni myślą o '{query}'.", "category": "opinions"},
            ]
            static_suggestions = static_suggestions_pl if language == 'pl' else static_suggestions_en

            # Shuffle static suggestions order for variety
            random.shuffle(static_suggestions)

            # System message for AI prompt
            system_lang = "Odpowiadaj wyłącznie po polsku." if language == 'pl' else "Answer in English."

            if is_specific:
                answer_prompt = f"""
                {system_lang}
                {context_text}Give a 4-part answer for '{query}': 
                (1) Name/description, 
                (2) short opinion/summary, 
                (3) price range, 
                (4) 1 suggestion for more specific search (if relevant).
                Respond ONLY with a JSON object: {{
                    'name': string, 
                    'description': [string, string, string], 
                    'source_info': string, 
                    'suggestions': [string], 
                    'actions': [{{'type': 'chat', 'label': 'Chaysh Assistant', 'query': '{query}'}}]
                }}
                """
                answer_response = await self.ask_ai(answer_prompt)
                try:
                    answer = self.extract_first_json(answer_response)
                    required_fields = {
                        'name': query,
                        'description': ['No description.', '', ''],
                        'source_info': 'AI-generated summary',
                        'suggestions': [],
                        'actions': [{'type': 'chat', 'label': 'Chaysh Assistant', 'query': query}]
                    }
                    for k, v in required_fields.items():
                        if k not in answer or not answer[k]:
                            answer[k] = v
                    ai_suggestion = answer['suggestions'][0] if answer['suggestions'] else ("Spróbuj wyszukać powiązany temat." if language == 'pl' else "Try searching for a related topic.")
                    suggestions = static_suggestions + [{"text": ai_suggestion, "category": "ai"}]
                    answer['suggestions'] = suggestions
                    return [answer]
                except Exception as e:
                    logging.error(f"Error parsing answer: {str(e)} | Response: {answer_response}")
            else:
                two_part_prompt = f"""
                {system_lang}
                {context_text}What is '{query}'? Give a 2-part answer: (1) product description, (2) 1 suggestion for more specific search (if relevant). Respond ONLY with a JSON object: {{'name': string, 'description': [string], 'source_info': string, 'suggestions': [string], 'actions': [{{'type': 'chat', 'label': 'Chaysh Assistant', 'query': '{query}'}}]}}
                """
                two_part_response = await self.ask_ai(two_part_prompt)
                try:
                    answer = self.extract_first_json(two_part_response)
                    required_fields = {
                        'name': query,
                        'description': ['No description.'],
                        'source_info': 'AI-generated summary',
                        'suggestions': [],
                        'actions': [{'type': 'chat', 'label': 'Chaysh Assistant', 'query': query}]
                    }
                    for k, v in required_fields.items():
                        if k not in answer or not answer[k]:
                            answer[k] = v
                    ai_suggestion = answer['suggestions'][0] if answer['suggestions'] else ("Spróbuj wyszukać powiązany temat." if language == 'pl' else "Try searching for a related topic.")
                    suggestions = static_suggestions + [{"text": ai_suggestion, "category": "ai"}]
                    answer['suggestions'] = suggestions
                    return [answer]
                except Exception as e:
                    logging.error(f"Error parsing 2-part answer: {str(e)} | Response: {two_part_response}")
            return [{
                'name': query,
                'description': [
                    f"Sorry, '{query}' is too broad or ambiguous." if language != 'pl' else f"Przepraszamy, '{query}' jest zbyt ogólne lub niejasne.",
                    "Try one of the suggestions below or specify a model/product." if language != 'pl' else "Spróbuj jednej z poniższych sugestii lub podaj model/produkt."
                ],
                'source_info': "No specific product found." if language != 'pl' else "Nie znaleziono konkretnego produktu.",
                'suggestions': static_suggestions + [{"text": "Spróbuj wyszukać powiązany temat." if language == 'pl' else "Try searching for a related topic.", "category": "ai"}],
                'actions': [
                    {'type': 'chat', 'label': 'Chaysh Assistant', 'query': query}
                ]
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
        """
        Extract the first valid JSON object from a string, even if extra text or code block is present.
        """
        try:
            text = text.strip()
            # Remove code block markers if present
            if text.startswith('```'):
                parts = text.split('```', 2)
                if len(parts) > 1:
                    text = parts[1]
                # Remove 'json' or other language tag if present
                if text.strip().lower().startswith('json'):
                    text = text.strip()[4:].strip()
            # Remove 'json' prefix if present (even outside code block)
            if text.strip().lower().startswith('json'):
                text = text.strip()[4:].strip()
            # Find the first {...} block
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group(0))
        except Exception as e:
            logging.error(f"Error extracting JSON: {str(e)} | Raw: {text}")
        return {}

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