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
Use AI (OpenAI or Cursor built-in) to interpret manuals’ text and provide clear step-by-step instructions

Allow users to ask natural language questions about product troubleshooting or features

Guide users interactively through manuals or tutorial steps

Provide explanations or clarifications as needed

Web Application
Clean, minimal, responsive UI built with Flask and Jinja2 templates

Search bar with auto-suggestions (future)

Search results page showing relevant manuals and snippets

Detail/assistant page showing extracted steps and AI walkthrough

Option to download or view original manuals (PDF or web)

3. Architecture and Tech Stack
Component	Technology / Approach
Backend Web App	Flask (Python)
Web Scraper	Requests + BeautifulSoup / Playwright (for JS-heavy sites)
Data Storage	SQLite with full-text search or Supabase/Postgres
AI Assistant	OpenAI API or Cursor AI integration
Search Index	SQLite FTS or Whoosh (lightweight search)
Frontend	Jinja2 templates with minimal JS for interaction
Deployment	Render Web Service
Source Control	GitHub (linked to Render for CI/CD)

4. File Structure (Example)
bash
Copy
Edit
/chaysh-manual-ai/
├── app.py                  # Flask app entry point
├── requirements.txt        # Python dependencies
├── build.sh                # Setup script for virtualenv and dependencies
├── Procfile                # For Render deployment
├── runtime.txt             # Python version (e.g. python-3.11.7)
├── .gitignore              # Ignore .venv, __pycache__, etc.
├── engine/
│   ├── crawler.py          # Web scraping logic with prioritized sites
│   ├── parser.py           # Parsing HTML/PDF manuals into text
│   └── assistant.py        # AI prompt handling & step-by-step logic
├── templates/
│   ├── index.html          # Search page
│   ├── results.html        # Search results display
│   └── assistant.html      # AI walkthrough page
└── static/                 # CSS and JS assets
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
Use the scraped manual text as context for AI prompts

Extract procedural steps clearly and concisely

Allow users to ask clarifying questions (e.g., “Explain step 3”)

Provide fallback answers if manual is missing or incomplete

Keep AI usage cost-effective by limiting tokens/context size

7. Deployment & Environment Setup
Use Python 3.11.7 (runtime.txt)

Setup a virtual environment during build (build.sh)

Install dependencies including Flask, gunicorn, openai, beautifulsoup4, requests, PyPDF2 (for PDFs)

Use Procfile to run gunicorn via the virtual environment:
.venv/bin/python -m gunicorn app:app --bind=0.0.0.0:$PORT --workers=2 --threads=2 --timeout=120

Build command on Render:
chmod +x build.sh && ./build.sh

Environment variables on Render for OpenAI API key and any secrets

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
Chaysh Manual AI will be a robust, easy-to-use web platform that combines:

Targeted web crawling for product manuals

AI-powered step-by-step guidance

A lightweight, stable Flask app deployed on Render

Search and assistant UI focused on real user needs

This document will guide all development phases and is the foundation for prompt engineering with Cursor Pro and further coding.
