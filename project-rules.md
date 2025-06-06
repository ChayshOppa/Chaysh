# Chaysh Project Rules (Updated March 2024)

## Core Architecture

### 1. AI Integration
- **OpenRouter API**: Primary AI engine for all responses
- **Response Format**: Standardized JSON structure for all AI responses:
  ```json
  {
    "basic_info": "Brief overview (max 100 chars)",
    "detailed_info": "Technical details (max 200 chars)",
    "product_info": "Specific features (max 200 chars)",
    "summary": "Concise conclusion (max 100 chars)"
  }
  ```

### 2. Language Support
- **Bilingual System**: Full support for English (en) and Polish (pl)
- **Language Detection**: Based on user's browser settings
- **Translation Rules**:
  - All UI elements are translated
  - AI responses are generated in the correct language
  - Suggestions are language-specific
  - Error messages are localized

### 3. Response Structure
- **Standard Fields**:
  ```json
  {
    "name": "query",
    "description": [
      "basic_info",
      "detailed_info",
      "product_info",
      "summary"
    ],
    "source_info": "source information",
    "suggestions": [
      {"text": "suggestion text", "category": "category"},
      ...
    ],
    "actions": [
      {"type": "chat", "label": "Chaysh Assistant", "query": "query"}
    ]
  }
  ```

### 4. Error Handling
- **API Errors**:
  - Invalid API key
  - Network issues
  - Rate limiting
  - Invalid responses
- **Response Processing**:
  - JSON validation
  - Field validation
  - Fallback responses
  - Error logging

## Implementation Details

### 1. Core Files
- `src/core/crawler.py`: OpenRouter integration and response processing
- `src/core/assistant.py`: AI response handling and formatting
- `src/core/config.py`: Configuration and environment settings
- `src/templates/home.html`: Frontend implementation

### 2. API Integration
- **OpenRouter Configuration**:
  - API key in `.env` file
  - Environment variable: `OPENROUTER_API_KEY`
  - Model: `anthropic/claude-3-opus-20240229`
  - Temperature: 0.7
  - Max tokens: 1000

### 3. Response Processing
- **Character Limits**:
  - Basic info: 100 chars
  - Detailed info: 200 chars
  - Product info: 200 chars
  - Summary: 100 chars
- **Validation Rules**:
  - All fields must be strings
  - No HTML or markdown
  - No special characters
  - Proper JSON formatting

### 4. Suggestions System
- **Static Suggestions**:
  - 4 suggestions per response
  - Categories: help, manual, model_search, opinions
  - Language-specific text
  - Context-aware formatting

## Development Rules

### 1. Code Standards
- Use type hints
- Implement error handling
- Add logging statements
- Follow PEP 8 style guide

### 2. Testing Requirements
- Test API integration
- Verify language switching
- Check response format
- Validate error handling

### 3. Documentation
- Update przypominajka.md after major changes
- Document API changes
- Keep response format documentation current
- Log all error cases

## Deployment

### 1. Environment Setup
- Python 3.11.7
- Required packages in requirements.txt
- Environment variables in .env
- Logging configuration

### 2. Server Configuration
- Uvicorn with debug mode
- Host: 0.0.0.0
- Port: 8000
- Log level: debug

## Backup and Recovery

### 1. Critical Files
- `src/core/crawler.py`
- `src/core/assistant.py`
- `src/core/config.py`
- `src/templates/home.html`
- `.env`

### 2. Recovery Process
1. Restore core files
2. Verify API key
3. Test language switching
4. Validate response format

## Future Development

### 1. Planned Features
- Enhanced error recovery
- Additional language support
- Improved response formatting
- Advanced suggestion logic

### 2. Maintenance Tasks
- Regular API key updates
- Log rotation
- Performance monitoring
- Error tracking

---

**Note**: This document is the source of truth for the project's implementation. All changes must be reflected here and in przypominajka.md.

## Search & Result Logic

- **All product search and result logic is now handled by a single OpenAI prompt.**
  - No scraping, intent analysis, or multi-step logic is used, and these approaches are no longer supported or maintained.
  - The backend sends a single, clear prompt to OpenAI based on query specificity (2-part for generic, 3-part for specific queries).
  - The backend robustly extracts the first valid JSON object from the OpenAI response, even if wrapped in code blocks or language tags.

- **The backend always returns a result object with these fields:**
  - `name`: The product or answer name (string)
  - `description`: A list of description strings (array of strings)
  - `source_info`: A string with source or summary info (string)
  - `suggestions`: A list of suggestions for further queries (array of strings)
  - `actions`: A list of action objects (array, always includes a Chaysh Assistant button)

- **If the OpenAI response is malformed or missing fields, the backend fills in all required fields with sensible defaults.**

- **The frontend only displays these fields:**
  - `name`, `description`, `source_info`, `suggestions`, `actions`
  - There are no references to legacy fields like `title`, `source`, `url`, or "View Manual".
  - The UI is modern, Tailwind-based, and only shows the new answer box, suggestions, and AI assistant button.

- **All templates and static files are modern, Tailwind-based, and reside in the main templates directory.**
  - No legacy Bootstrap, Font Awesome, or old CSS is used.
  - Only the new fields and design are present in the UI.

- **All unnecessary, duplicate, or legacy files have been removed.**

## Base for Future Development
- The current AI-driven search and result logic is the new base for all future development.
- No scraping or legacy approaches will be reintroduced.
- All new features and improvements will build on this unified, AI-based approach.

## Summary
- The system is now streamlined, robust, and easy to maintain.
- All search and result logic is AI-driven, with a single prompt and a unified result object.
- The frontend and backend are fully aligned, with no legacy code or UI remaining.

1. Project Overview
Name: Chaysh (Manual AI)
Purpose: Build a specialized AI-powered search engine and assistant for product manuals, guides, and tutorials.
Goal: Help users quickly find official manuals and step-by-step instructions for various products, and interactively guide them through solutions.

2. Core Features
Search & Crawl
Crawl and index official manufacturer websites (e.g., samsung.com/manuals, hp.com/support)

Include major manual libraries like manualslib.com, manuals.plus, manualowl.com

Support search queries by product name, model number, or keywords

Prioritize official sources over third-party sites

Extract textual content from webpages and PDFs where possible

AI Assistant
Use OpenRouter API for AI-powered step-by-step help and explanations (free for testing)

Use the scraped manual text as context for AI prompts

Allow users to ask natural language questions about product troubleshooting or features

Guide users interactively through manuals or tutorial steps

Provide explanations or clarifications as needed

Web Application
Clean, minimal, responsive UI built with FastAPI, Jinja2 templates, and modular CSS (dark grey & gold theme)

Search bar with auto-suggestions (future)

Search results page showing relevant manuals and snippets

Detail/assistant page showing extracted steps and AI walkthrough

Option to download or view original manuals (PDF or web)

3. Architecture and Tech Stack
Component	Technology / Approach
Backend Web App	FastAPI (Python)
Web Scraper	Requests + BeautifulSoup / Playwright (for JS-heavy sites)
Data Storage	SQLite with full-text search or Supabase/Postgres
AI Assistant	OpenRouter API (for free AI assistant)
Search Index	SQLite FTS or Whoosh (lightweight search)
Frontend	Jinja2 templates, modular CSS, minimal JS for interaction
Deployment	Render Web Service
Source Control	GitHub (linked to Render for CI/CD)

4. File Structure (Example)
bash
Copy
Edit
/chaysh-manual-ai/
├── src/
│   ├── main.py                # FastAPI app entry point
│   ├── core/
│   │   ├── config.py          # App settings
│   │   ├── assistant.py       # AI prompt handling & step-by-step logic
│   │   ├── search.py          # Search logic
│   │   └── crawler.py         # Web scraping logic
│   ├── templates/
│   │   ├── base.html          # Base template (dark/gold theme)
│   │   ├── home.html          # Home/search page
│   │   └── ...                # Other pages
│   └── static/                # CSS and JS assets
├── requirements.txt           # Python dependencies
├── Procfile                   # For Render deployment
├── runtime.txt                # Python version (e.g. python-3.11.7)
├── .gitignore                 # Ignore .venv, __pycache__, etc.

5. Crawling & Data Collection Rules
Begin crawling from a defined seed list of domains prioritized by:

Official manufacturer support/manual domains

Trusted manual libraries (manualslib.com, manuals.plus, etc.)

Other product help/tutorial sites as fallback

Scrape only manual-related content (manuals, guides, FAQs)

Avoid scraping unrelated pages (blogs, news, unrelated products)

Respect robots.txt and site terms of service

Handle PDFs by downloading and extracting text if possible

Update crawl schedule periodically for fresh content

6. AI Assistant Rules
Use OpenRouter API for all AI assistant features (free for testing)

Use the scraped manual text as context for AI prompts

Extract procedural steps clearly and concisely

Allow users to ask clarifying questions (e.g., "Explain step 3")

Provide fallback answers if manual is missing or incomplete

Keep AI usage cost-effective by limiting tokens/context size

7. Deployment & Environment Setup
Use Python 3.11.7 (runtime.txt)

Setup a virtual environment during build (build.sh)

Install dependencies including FastAPI, gunicorn, openai, beautifulsoup4, requests, PyPDF2 (for PDFs), jinja2, whoosh

Use Procfile to run gunicorn via the virtual environment:
.venv/bin/python -m gunicorn src.main:app --bind=0.0.0.0:$PORT --workers=2 --threads=2 --timeout=120

Build command on Render:
chmod +x build.sh && ./build.sh

Environment variables on Render for OpenRouter API key and any secrets

Logging and error monitoring for scraper and web app

8. Development and Collaboration Rules
All code pushed to GitHub repo linked to Render for automatic deploy

Feature branches for new features or fixes

PR review process before merging to main branch

Write tests for scraper and API where possible

Document all key functions and components

9. Future Expansion Ideas
Mobile app or PWA frontend

User accounts with saved manuals or search history

Multilingual manual support and translation

User manual uploads and community contributions

AI chatbot for troubleshooting with memory and personalization

10. Summary
Chaysh Manual AI is a robust, easy-to-use web platform that combines:

Targeted web crawling for product manuals

AI-powered step-by-step guidance (via OpenRouter API)

A lightweight, stable FastAPI app deployed on Render

Search and assistant UI focused on real user needs

This document guides all development phases and is the foundation for prompt engineering and further coding.

11. Current Project Status (Updated)
Working Components:
- Basic FastAPI application structure is set up and running
- Local development environment is configured with Python 3.11.6
- Core dependencies are installed and working
- Basic web interface is accessible at http://127.0.0.1:8000
- Manual crawler is operational and fetches results from manualslib.com using the correct URL pattern: /[first_letter]/[keyword].html
- Search results are limited to 50 and the top 10 best hits are returned to the user

Next Steps:
1. Implement the search functionality
2. Set up the web scraper for manual collection
3. Integrate OpenRouter API for AI assistance
4. Develop the UI with dark grey & gold theme
5. Set up the database for storing manuals

Development Environment:
- Python 3.11.6
- Virtual environment (.venv)
- FastAPI with uvicorn for local development
- Dependencies managed via requirements.txt

Local Setup Instructions:
1. Create virtual environment: python -m venv .venv
2. Activate environment: .\.venv\Scripts\activate
3. Install dependencies: pip install -r requirements.txt
4. Run application: python run.py
5. Access at: http://127.0.0.1:8000 

12. Consensus Aggregation Approach (2024-05)
Chaysh now searches 3 different links for each query, extracts product description, rating, and price, and uses OpenRouter to generate a single neutral summary that reflects the consensus of all 3 sources. Only one result is returned, with links to all 3 sources. This reduces API usage and improves reliability.

### AI Assistant Progress (May 2024)
- Fully integrated OpenRouter API for all assistant responses.
- Bilingual support (English/Polish) for both UI and AI answers.
- Standardized JSON response format enforced and validated.
- Robust error handling for API/network issues and malformed responses.
- Assistant UI is modern, Tailwind-based, and supports both light and dark themes.
- Language switching is persistent and respected across all assistant interactions.
- All assistant actions and suggestions are language-aware and contextually relevant.
- No legacy/manual scraping logic remains; all results are AI-driven.
- Ongoing: UI polish for light/dark mode separation in chat area. 