from flask import Flask, render_template, request, jsonify
from core.assistant import Assistant
from core.crawler import search_manuals
from core.storage import LocalStorage
import asyncio
import logging
from flask_cors import CORS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
assistant = Assistant()
storage = LocalStorage()

def get_system_prompt(language):
    prompts = {
        'pl': 'Odpowiadaj wyłącznie po polsku. Ignoruj inne języki.',
        'en': 'Answer only in English. Ignore other languages.',
        # Add more languages as needed
    }
    return prompts.get(language, prompts['en'])

@app.route('/')
def home():
    # Get user preferences for initial page load
    preferences = storage.get_preferences()
    return render_template('home.html', preferences=preferences)

@app.route('/assistant')
def assistant_page():
    # Get user preferences and chat history
    preferences = storage.get_preferences()
    chat_history = storage.get_chat_history()
    return render_template('assistant.html', preferences=preferences, chat_history=chat_history)

@app.route('/api/search', methods=['POST'])
def handle_search():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        query = data.get('query', '')
        context = data.get('context', [])
        language = data.get('language', 'en')
        
        if not query:
            return jsonify({'error': 'No search query provided'}), 400
        
        logger.info(f"Processing search: {query} in language: {language}")
        
        # Run the async function in the event loop
        results = asyncio.run(search_manuals(query, context=context, language=language))
        
        # Save search results to local storage
        storage.save_search(query, results, language)
        
        if not results:
            return jsonify({
                "success": False,
                "error": "No results found",
                "results": [{
                    'name': query,
                    'description': ['No results found for your search.'],
                    'source_info': 'Search returned no results',
                    'suggestions': [],
                    'actions': [{'type': 'chat', 'label': 'Chaysh Assistant', 'query': query}]
                }]
            })
        
        return jsonify({
            "success": True,
            "results": results
        })
    except Exception as e:
        logger.error(f"Error in handle_search: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e),
            "results": [{
                'name': query,
                'description': ['An error occurred while processing your search.'],
                'source_info': 'Error processing request',
                'suggestions': [],
                'actions': [{'type': 'chat', 'label': 'Chaysh Assistant', 'query': query}]
            }]
        })

@app.route('/api/assistant', methods=['POST'])
def handle_assistant():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        message = data.get('message', '')
        language = data.get('language', 'en')
        
        if not message or len(message) > 100:
            return jsonify({'error': 'Invalid message length'}), 400
        
        logger.info(f"Processing message: {message} in language: {language}")
        
        # Run the async function in the event loop
        system_prompt = get_system_prompt(language)
        response = asyncio.run(assistant.generate_response(system_prompt + '\n' + message, {'language': language}))
        
        # Save chat to local storage
        storage.save_chat(message, response, language)
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in handle_assistant: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/preferences', methods=['GET', 'POST'])
def handle_preferences():
    if request.method == 'GET':
        return jsonify(storage.get_preferences())
    else:
        try:
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            storage.update_preferences(data)
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}", exc_info=True)
            return jsonify({'error': str(e)}), 500

@app.route('/api/favorites', methods=['POST'])
def handle_favorites():
    try:
        data = request.json
        if not data or 'result' not in data:
            return jsonify({'error': 'No result provided'}), 400
        storage.add_favorite_result(data['result'])
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error adding favorite: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        logger.info("Starting Flask server...")
        app.run(host='0.0.0.0', port=8000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}", exc_info=True) 