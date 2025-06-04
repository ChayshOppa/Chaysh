from flask import Flask, render_template, request, redirect, url_for, flash
from engine.crawler import Crawler
from engine.parser import Parser
from engine.assistant import Assistant
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flash messages

# Initialize components
crawler = Crawler()
parser = Parser()
assistant = Assistant()

@app.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')

@app.route('/search')
def search():
    """Handle search requests."""
    query = request.args.get('q', '').strip()
    
    if not query:
        flash('Please enter a search query')
        return redirect(url_for('home'))
    
    logger.info(f"Processing search query: {query}")
    
    try:
        # For now, return mock results
        # TODO: Implement actual search functionality
        results = [
            {
                'title': 'Sample Manual 1',
                'snippet': 'This is a sample manual for testing purposes.',
                'source': 'example.com'
            },
            {
                'title': 'Sample Manual 2',
                'snippet': 'Another sample manual for testing.',
                'source': 'example.org'
            }
        ]
        
        return render_template(
            'results.html',
            query=query,
            results=results,
            stats={'total_results': len(results)}
        )
    except Exception as e:
        logger.error(f"Error processing search: {str(e)}", exc_info=True)
        flash('An error occurred while processing your search. Please try again.')
        return render_template('error.html', message=str(e))

@app.route('/assistant')
def assistant_route():
    """Handle AI assistant queries."""
    query = request.args.get('query', '').strip()
    
    if not query:
        flash('Please enter a query for the assistant')
        return redirect(url_for('home'))
    
    logger.info(f"Processing assistant query: {query}")
    
    try:
        # For now, return a mock response
        # TODO: Implement actual AI assistant functionality
        response = {
            'response': f'Here\'s what I found about {query}. This is a placeholder response - AI integration coming soon.',
            'steps': [
                'Step 1: This is a placeholder step',
                'Step 2: AI-generated steps will be available soon'
            ]
        }
        
        return render_template('assistant.html', query=query, response=response)
    except Exception as e:
        logger.error(f"Error in assistant: {str(e)}", exc_info=True)
        return render_template('error.html', message=str(e))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message='Page not found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', message='Internal server error'), 500

if __name__ == '__main__':
    # This block will only run when the script is executed directly
    # In production, gunicorn will handle the server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 