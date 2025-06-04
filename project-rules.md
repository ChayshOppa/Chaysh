# Project Rules for Chaysh Search Engine

## General Purpose
- Build a web-based AI-powered search assistant called "Chaysh"
- It scrapes free public websites with manuals, product info, guides, etc.
- Provides summarized, AI-generated user-friendly answers based on multiple sources
- Initially supports IKEA manuals as a proof of concept, but designed for easy extension to many sites

## Architecture
- Backend: Python Flask web server  
- Frontend: Minimal but clean HTML templates with Flask Jinja2  
- Scraper module: Modular scrapers for each source website, returning unified structured data  
- AI assistant: Uses pre-existing AI APIs or local AI models to generate responses based on scraped data

## Features & Flow
1. User visits homepage with a search box  
2. User submits a query  
3. Backend scrapes configured websites for that query (limit results, e.g. top 10)  
4. Display a search results page listing found items (title + short snippet + link)  
5. User clicks on one result to open an AI assistant page with detailed, summarized info  
6. AI assistant answers with clear, concise explanation derived from all relevant scraped content  

## Scraper Guidelines
- Scraper must support multiple sites, with separate functions/classes for each  
- Return data in a consistent format:  
  `{ title: str, snippet: str, link: str }`  
- Handle failures gracefully (no results, site structure changes)  
- Respect robots.txt and legal terms — only scrape publicly available content  
- Start with IKEA search as initial scraper example, later add more sources

## Coding Practices
- Write clear, commented code  
- Step-by-step modular implementation — build minimum viable features first  
- Use Python 3.13+ and latest Flask  
- Avoid blocking calls, optimize for performance where possible  
- Create reusable templates and separate logic from presentation

## Testing & Deployment
- Test locally with Flask dev server  
- Provide instructions for running and extending  
- Prepare for future production deployment (not immediate priority)  

## Interaction with User (You)
- Wait for clear confirmation before proceeding to next step  
- Explain each step with code + instructions + testing notes  
- Provide code as ready-to-paste files or snippets for your environment  
- Support iterative improvements based on feedback  

---
