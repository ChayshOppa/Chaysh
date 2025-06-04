from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import List, Optional

from core.config import get_settings
from core.assistant import Assistant
from core.search import SearchEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chaysh API",
    description="AI-powered manual search and assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
settings = get_settings()
assistant = Assistant()
search_engine = SearchEngine()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Chaysh API"}

@app.get("/search")
async def search(query: str = Query(..., min_length=2)):
    """
    Search for manual content.
    
    Args:
        query: Search query (minimum 2 characters)
        
    Returns:
        List of search results
    """
    try:
        results = await search_engine.search(query)
        return {
            "query": query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/assistant")
async def get_assistant_response(
    query: str = Query(..., min_length=2),
    context_url: Optional[str] = None
):
    """
    Get AI assistant response.
    
    Args:
        query: User's question
        context_url: Optional URL to provide context
        
    Returns:
        AI response with steps
    """
    try:
        context = None
        if context_url:
            # Get context from the URL
            success = await search_engine.crawl_and_index(context_url)
            if success:
                results = await search_engine.search(query, limit=1)
                if results:
                    context = results[0]
        
        response = await assistant.generate_response(query, context)
        return response
    except Exception as e:
        logger.error(f"Error in assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crawl")
async def crawl_url(url: str):
    """
    Crawl and index a URL.
    
    Args:
        url: URL to crawl
        
    Returns:
        Success status
    """
    try:
        success = await search_engine.crawl_and_index(url)
        if success:
            return {"message": "URL crawled and indexed successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to crawl URL")
    except Exception as e:
        logger.error(f"Error crawling URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    ) 