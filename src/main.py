from fastapi import FastAPI, HTTPException, Query, Request, Response, Cookie, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
import os
import uuid
from starlette.middleware.sessions import SessionMiddleware
import json
import asyncio
import re
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup

from .core.config import get_settings
from .core.assistant import Assistant
from .core.database import Database
from .core.crawler import search_manuals

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with detailed logging
app = FastAPI(
    title="Chaysh - Manual Search & AI Assistant",
    description="AI-powered manual search and assistant",
    version="1.0.0",
    debug=True  # Enable debug mode for more detailed error messages
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware with secure key
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "your-secret-key"),
    session_cookie="chaysh_session",
    max_age=3600  # 1 hour
)

# Add logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}", exc_info=True)
        raise

# Get the absolute path to the static directory
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

# Mount static files with absolute path
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Initialize templates with absolute path
templates = Jinja2Templates(directory=str(templates_dir))

# Initialize components
settings = get_settings()
assistant = Assistant()

# Initialize database
db = Database()

class SearchQuery(BaseModel):
    query: str
    context: Optional[List[str]] = None
    language: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict] = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/assistant")
async def assistant_page(request: Request, q: Optional[str] = None):
    """Assistant page endpoint."""
    return templates.TemplateResponse("assistant.html", {
        "request": request,
        "query": q
    })

@app.post("/api/search")
async def search(request: Request, query: SearchQuery, x_language: str = Header(None)):
    logging.info(f"Received search request: {query.query}")
    logging.info(f"Language header: {x_language}")
    
    # Get context from request if available
    context_prompts = None
    try:
        body = await request.json()
        context_prompts = body.get('context')
        logging.info(f"Context from request: {context_prompts}")
    except:
        logging.info("No context provided in request")
    
    # Determine language
    language = x_language if x_language in ['en', 'pl'] else 'en'
    logging.info(f"Using language: {language}")
    
    try:
        logging.info("Calling search_manuals...")
        # Use the crawler's search_manuals function for AI-powered search
        results = await search_manuals(query.query, context=context_prompts, language=language)
        logging.info(f"Raw search results: {results}")
        
        if not results:
            logging.warning("No results returned from search_manuals")
            return {
                "success": False,
                "error": "No results found",
                "results": [{
                    'name': query.query,
                    'description': ['No results found for your search.'],
                    'source_info': 'Search returned no results',
                    'suggestions': [],
                    'actions': [{'type': 'chat', 'label': 'Chaysh Assistant', 'query': query.query}]
                }]
            }
        
        search_id = db.log_search(query.query, len(results))
        logging.info(f"Search logged with ID: {search_id}")
        
        # Ensure each result has the required fields
        for result in results:
            if not isinstance(result, dict):
                logging.error(f"Invalid result format: {result}")
                continue
                
            if 'name' not in result or not result['name']:
                result['name'] = query.query
            if 'description' not in result or not result['description']:
                result['description'] = ['No description available.']
            if 'source_info' not in result or not result['source_info']:
                result['source_info'] = 'AI-generated summary'
            if 'suggestions' not in result or not result['suggestions']:
                result['suggestions'] = []
            if 'actions' not in result or not result['actions']:
                result['actions'] = [{'type': 'chat', 'label': 'Chaysh Assistant', 'query': query.query}]
            
            # Ensure description is a list
            if isinstance(result['description'], str):
                result['description'] = [result['description']]
            elif not isinstance(result['description'], list):
                result['description'] = ['No description available.']
        
        response_data = {
            "success": True,
            "search_id": search_id,
            "results": results
        }
        logging.info(f"Sending response: {response_data}")
        return response_data
        
    except Exception as e:
        logging.error(f"Error in search endpoint: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "results": [{
                'name': query.query,
                'description': ['An error occurred while processing your search.'],
                'source_info': 'Error processing request',
                'suggestions': [],
                'actions': [{'type': 'chat', 'label': 'Chaysh Assistant', 'query': query.query}]
            }]
        }

@app.post("/api/chat")
async def chat(message: ChatMessage):
    try:
        response = await assistant.generate_response(
            message.message,
            context=message.context
        )
        if 'error' in response:
            return {
                "success": False,
                "error": response['error'],
                "response": response['response']
            }
        return {
            "success": True,
            "response": response['response'],
            "steps": response.get('steps', [])
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "response": "Sorry, I encountered an error while processing your message."
        }

@app.get("/api/stats")
async def get_stats():
    """Get application statistics."""
    try:
        stats = {
            "total_searches": db.get_total_searches(),
            "total_results": db.get_total_results(),
            "average_results": db.get_average_results()
        }
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=get_settings().HOST,
        port=get_settings().PORT,
        reload=not get_settings().DEBUG
    ) 