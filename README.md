# Chaysh - Manual Search & AI Assistant

Chaysh is an AI-powered manual search and assistant application that helps users find and understand product manuals and documentation.

## Features

- AI-powered search for product manuals
- Interactive chat assistant
- Multi-language support (English and Polish)
- Real-time search suggestions
- User opinions and ratings
- Manual categorization and organization

## Tech Stack

- Backend: FastAPI (Python)
- Frontend: HTML, CSS, JavaScript
- AI: OpenRouter API (GPT-3.5)
- Database: SQLite (async)
- Search: Whoosh
- Deployment: Render

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chaysh.git
cd chaysh
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file:
```bash
cp .env.example .env
```

5. Update the .env file with your OpenRouter API key:
```
OPENROUTER_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

6. Run the development server:
```bash
uvicorn src.main:app --reload
```

The application will be available at http://localhost:8000

## Development

- Run tests: `pytest`
- Format code: `black .`
- Sort imports: `isort .`
- Lint code: `flake8`

## Deployment

The application is configured for deployment on Render. The `render.yaml` file contains the necessary configuration.

## License

MIT License 