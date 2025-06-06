from fastapi import FastAPI, HTTPException, Query, Request, Response, Cookie, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
import os
import uuid
from starlette.middleware.sessions import SessionMiddleware

from .core.config import get_settings
from .core.assistant import Assistant
from .core.search import SearchEngine
from .core.crawler import search_manuals
from .core.database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chaysh - Manual Search & AI Assistant",
    description="AI-powered manual search and assistant",
    version="1.0.0"
)

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

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
search_engine = SearchEngine()

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

@app.post("/api/search")
async def search(request: Request, query: SearchQuery, x_language: str = Header(None)):
    session = request.session
    # Determine language: header > body > session > default
    language = x_language or getattr(query, 'language', None) or session.get('language', 'en')
    session['language'] = language
    logging.info(f"Language for this request: {language}")
    prompts = session.get("prompts", [])
    prompts.append(query.query)
    if len(prompts) > 5:
        prompts = prompts[-5:]
    session["prompts"] = prompts
    context_prompts = prompts[-3:]
    try:
        # Pass context_prompts and language to search_manuals for context-aware suggestions
        results = await search_manuals(query.query, context=context_prompts, language=language)
        search_id = db.log_search(query.query, len(results))
        logging.info(f"Search result: {results}")
        return {
            "success": True,
            "search_id": search_id,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(message: ChatMessage):
    try:
        response = await assistant.generate_response(
            message.message,
            context=message.context
        )
        return {
            "success": True,
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    try:
        stats = db.get_search_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return HTMLResponse(
        status_code=500,
        content="An error occurred. Please try again later."
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 