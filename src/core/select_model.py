from typing import List, Dict, Optional
import logging

class ModelSelector:
    def __init__(self, ai_client):
        self.ai_client = ai_client

    async def get_model_variations(self, query: str) -> Dict:
        """
        Get a list of model variations for a given query.
        Returns a dictionary with variations list and is_specific flag.
        """
        try:
            variations_prompt = f"""
            You are a product expert. For the query: {query}

            Task: Generate a list of specific models, variations, or options that would help narrow down the search.
            
            Rules:
            1. For general terms (like "iphone"), list specific models
            2. For specific models (like "iphone 15 pro max"), return empty list
            3. For products with few options (like "knockout midi controller"), list available versions
            4. For products with many options, list the most relevant ones (max 20)
            5. Each variation should be specific enough to create a new detailed search

            Examples:
            - For "iphone": list specific iPhone models
            - For "knockout midi controller": list available versions (1, 2, extra)
            - For "guitar": list popular types (acoustic, electric, bass)
            - For "camera": list popular brands and models
            - For "laptop": list popular brands and series

            Respond in JSON format:
            {{
                "variations": [
                    {{
                        "name": "Specific model/version name",
                        "query": "Search query to use for this specific model"
                    }}
                ],
                "is_specific": boolean,
                "category": "string (e.g., 'smartphone', 'midi_controller', 'camera')"
            }}

            Example for "iphone":
            {{
                "variations": [
                    {{"name": "iPhone 15 Pro Max", "query": "iphone 15 pro max"}},
                    {{"name": "iPhone 15 Pro", "query": "iphone 15 pro"}},
                    {{"name": "iPhone 15 Plus", "query": "iphone 15 plus"}},
                    {{"name": "iPhone 15", "query": "iphone 15"}}
                ],
                "is_specific": false,
                "category": "smartphone"
            }}

            Example for "knockout midi controller":
            {{
                "variations": [
                    {{"name": "Knockout 2", "query": "knockout 2 midi controller"}},
                    {{"name": "Knockout 1", "query": "knockout 1 midi controller"}},
                    {{"name": "Knockout Extra", "query": "knockout extra midi controller"}}
                ],
                "is_specific": false,
                "category": "midi_controller"
            }}

            Example for "iphone 15 pro max":
            {{
                "variations": [],
                "is_specific": true,
                "category": "smartphone"
            }}
            """

            response = await self.ai_client.ask_ai(variations_prompt)
            variations_data = self.ai_client.extract_first_json(response)

            if not variations_data:
                # Return empty variations if AI response fails
                return {
                    "variations": [],
                    "is_specific": True,
                    "category": "unknown"
                }

            return variations_data

        except Exception as e:
            logging.error(f"Error in get_model_variations: {str(e)}", exc_info=True)
            return {
                "variations": [],
                "is_specific": True,
                "category": "unknown"
            } 