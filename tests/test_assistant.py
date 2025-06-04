import pytest
from src.core.assistant import Assistant
from src.core.config import get_settings

@pytest.fixture
def assistant():
    return Assistant()

@pytest.mark.asyncio
async def test_generate_response(assistant):
    """Test basic response generation."""
    query = "How do I reset my router?"
    response = await assistant.generate_response(query)
    
    assert isinstance(response, dict)
    assert "response" in response
    assert isinstance(response["response"], str)
    assert len(response["response"]) > 0

@pytest.mark.asyncio
async def test_generate_response_with_context(assistant):
    """Test response generation with context."""
    query = "How do I reset my router?"
    context = {
        "title": "Router Manual",
        "content": "To reset the router, press and hold the reset button for 10 seconds."
    }
    
    response = await assistant.generate_response(query, context)
    
    assert isinstance(response, dict)
    assert "response" in response
    assert isinstance(response["response"], str)
    assert len(response["response"]) > 0
    assert "steps" in response
    assert isinstance(response["steps"], list)

@pytest.mark.asyncio
async def test_error_handling(assistant):
    """Test error handling with invalid API key."""
    # Temporarily set invalid API key
    settings = get_settings()
    original_key = settings.OPENROUTER_API_KEY
    settings.OPENROUTER_API_KEY = "invalid_key"
    
    query = "How do I reset my router?"
    response = await assistant.generate_response(query)
    
    # Restore original API key
    settings.OPENROUTER_API_KEY = original_key
    
    assert isinstance(response, dict)
    assert "error" in response
    assert isinstance(response["error"], str) 