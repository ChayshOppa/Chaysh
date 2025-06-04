#!/bin/bash
set -o errexit  # Fail fast on errors

# Print environment information
echo "=== Environment Information ==="
python --version
python -m pip --version
which python
which pip
echo "PATH: $PATH"
echo "PYTHONPATH: $PYTHONPATH"
echo "============================"

# Upgrade pip and install dependencies
echo "=== Installing Dependencies ==="
python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Ensure gunicorn is installed and verify
echo "=== Installing and Verifying Gunicorn ==="
pip install --no-cache-dir gunicorn==21.2.0
python -m gunicorn --version
which gunicorn || echo "gunicorn not found in PATH"

# Create necessary directories
echo "=== Creating Directories ==="
mkdir -p logs

# Print final environment check
echo "=== Final Environment Check ==="
echo "Python location: $(which python)"
echo "Pip location: $(which pip)"
echo "Gunicorn location: $(which gunicorn || echo 'not found')"
echo "============================" 