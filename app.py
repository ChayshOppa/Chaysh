from flask import Flask, render_template, request, redirect, url_for, flash
from scrapers.unified_scraper import UnifiedScraper
import logging
import os
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flash messages
scraper = UnifiedScraper()

@app.route('/')
def home():
    """Render the home page."""
    return render_template('home.html')

@app.route('/search')
def search():
    """Handle search requests."""
    query = request.args.get('q', '').strip()
    
    if not query:
        flash('Please enter a search query')
        return redirect(url_for('home'))
    
    logger.info(f"Processing search query: {query}")
    
    try:
        results = scraper.search(query)
        logger.info(f"Found {len(results)} results")
        
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
def assistant():
    """Handle AI assistant queries."""
    query = request.args.get('query', '').strip()
    
    if not query:
        flash('Please enter a query for the assistant')
        return redirect(url_for('home'))
    
    logger.info(f"Processing assistant query: {query}")
    
    # For now, return a simple response with the query
    # TODO: Implement AI assistant integration
    response = {
        'title': query,
        'summary': f'Here\'s what I found about {query}. This is a placeholder response - AI integration coming soon.',
        'tips': [
            'This is a placeholder tip',
            'AI-generated tips will be available soon'
        ],
        'warnings': [
            'This is a placeholder warning',
            'AI-generated warnings will be available soon'
        ]
    }
    
    return render_template('assistant.html', query=query, response=response)

@app.route('/debug')
def debug():
    """Show scraper status and test results."""
    try:
        # Get scraper status
        scraper_status = scraper.get_status()
        
        # Load test results if available
        test_results = {}
        try:
            with open('unified_test_results.json', 'r') as f:
                test_data = json.load(f)
                test_results = test_data.get('queries', {})
        except FileNotFoundError:
            logger.warning("No test results file found")
        
        return render_template(
            'debug.html',
            scraper_status=scraper_status,
            test_results=test_results
        )
    except Exception as e:
        logger.error(f"Error in debug page: {str(e)}", exc_info=True)
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