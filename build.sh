#!/usr/bin/env bash
set -o errexit

echo "Creating virtual environment"
python -m venv .venv
source .venv/bin/activate

echo "Upgrading pip and installing dependencies"
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -r requirements.txt

echo "Creating necessary directories"
mkdir -p data/index
mkdir -p logs

echo "Verifying installation"
python -c "import fastapi; import uvicorn; import httpx; import beautifulsoup4; import whoosh" 