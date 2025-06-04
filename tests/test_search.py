import pytest
from src.core.search import SearchEngine

@pytest.fixture
def search_engine():
    return SearchEngine()

@pytest.mark.asyncio
async def test_search_empty_index(search_engine):
    """Test search with empty index."""
    results = await search_engine.search("test query")
    assert isinstance(results, list)
    assert len(results) == 0

@pytest.mark.asyncio
async def test_crawl_and_index(search_engine):
    """Test crawling and indexing a URL."""
    # Use a test URL that's likely to be a manual
    url = "https://www.ikea.com/us/en/customer-service/product-support/assembly-instructions/"
    success = await search_engine.crawl_and_index(url)
    assert success is True

@pytest.mark.asyncio
async def test_search_after_indexing(search_engine):
    """Test search after indexing content."""
    # First index some content
    url = "https://www.ikea.com/us/en/customer-service/product-support/assembly-instructions/"
    await search_engine.crawl_and_index(url)
    
    # Then search
    results = await search_engine.search("assembly instructions")
    assert isinstance(results, list)
    assert len(results) > 0
    
    # Check result structure
    result = results[0]
    assert "title" in result
    assert "content" in result
    assert "url" in result
    assert "source" in result

def test_is_manual_page(search_engine):
    """Test manual page detection."""
    # Test with manual-like URL and content
    url = "https://example.com/manual"
    content = "This is a user manual for the product."
    assert search_engine.is_manual_page(url, content) is True
    
    # Test with non-manual URL and content
    url = "https://example.com/blog"
    content = "This is a blog post about something else."
    assert search_engine.is_manual_page(url, content) is False 