# Chaysh Manual AI

Chaysh Manual AI is a web application that helps users find and understand product manuals using AI-powered search and assistance.

## Features

- Web crawling for product manuals
- AI-powered search functionality
- Intelligent parsing of manual content
- AI assistant for answering questions about products
- Modern, responsive web interface

## Project Structure

```
chaysh/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Procfile           # For Render deployment
├── build.sh           # Build script for Render
├── runtime.txt        # Python runtime version
├── engine/            # Core functionality
│   ├── crawler.py     # Web crawling module
│   ├── parser.py      # Content parsing module
│   └── assistant.py   # AI assistant module
├── static/            # Static files
│   ├── css/          # Stylesheets
│   └── js/           # JavaScript files
└── templates/         # HTML templates
    ├── index.html    # Home page
    ├── results.html  # Search results
    └── assistant.html # AI assistant interface
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
   OPENAI_API_KEY=your_api_key_here
   ```

5. Run the development server:
   ```bash
   python app.py
   ```

## Deployment

The application is configured for deployment on Render. The `build.sh` script and `Procfile` handle the deployment process automatically.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 