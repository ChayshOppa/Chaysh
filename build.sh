#!/bin/bash
set -o errexit  # Fail fast on errors

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Ensure gunicorn is installed and executable
pip install --no-cache-dir gunicorn==21.2.0

# Create necessary directories
mkdir -p logs 