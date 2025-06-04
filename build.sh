#!/usr/bin/env bash
set -o errexit

echo "Creating virtual environment"
python -m venv .venv
source .venv/bin/activate

echo "Upgrading pip and installing dependencies"
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -r requirements.txt

echo "Verifying gunicorn installation"
python -m gunicorn --version

echo "Creating necessary directories"
mkdir -p logs
mkdir -p static/css
mkdir -p static/js 