# Chaysh Manual AI

Chaysh is an AI-powered search engine and assistant specialized in finding and explaining product manuals, tutorials, and help content.

## Features

- 🔍 **Smart Search Engine**
  - Automatically finds and indexes manual content
  - Prioritizes official sources and high-quality content
  - Clean, organized search results

- 🤖 **AI Assistant**
  - Powered by OpenRouter API (GPT-4-mini or LLaMA3)
  - Provides step-by-step guidance
  - Uses scraped content for context-aware responses

## Tech Stack

- **Backend**: FastAPI (Python)
- **AI**: OpenRouter API
- **Search**: Whoosh
- **Web Scraping**: httpx + BeautifulSoup4
- **Deployment**: Render

## Project Structure

```
chaysh/
├── src/
│   ├── core/
│   │   ├── config.py     # Configuration and settings
│   │   ├── assistant.py  # AI assistant implementation
│   │   └── search.py     # Search engine implementation
│   └── main.py          # FastAPI application
├── data/
│   └── index/           # Search index storage
├── tests/               # Test files
├── requirements.txt     # Python dependencies
└── .env                # Environment variables
```

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/chaysh.git
   cd chaysh
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file with:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   MODEL_NAME=gpt-4-mini  # or llama-3-70b-instruct
   LOG_LEVEL=INFO
   ```

5. Run the development server:
   ```bash
   uvicorn src.main:app --reload
   ```

## API Endpoints

- `GET /`: Root endpoint
- `GET /search?query=...`: Search for manual content
- `GET /assistant?query=...&context_url=...`: Get AI assistant response
- `POST /crawl?url=...`: Crawl and index a URL

## Development

- Run tests: `pytest`
- Format code: `black src/`
- Sort imports: `isort src/`
- Lint code: `flake8 src/`

## Deployment

The application is configured for deployment on Render. The build process is automated through Render's build system.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 