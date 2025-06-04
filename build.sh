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

echo "=== Environment Information ==="
python --version
python -m pip --version
which python
which pip
echo "PATH: $PATH"
echo "PYTHONPATH: $PYTHONPATH"
echo "============================"

echo "=== Final Environment Check ==="
echo "Python location: $(which python)"
echo "Pip location: $(which pip)"
echo "Gunicorn location: $(which gunicorn || echo 'not found')"
echo "Virtual Environment: $VIRTUAL_ENV"
echo "============================" 