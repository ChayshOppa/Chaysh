#!/usr/bin/env bash
set -o errexit

echo "=== Creating Virtual Environment ==="
python -m venv .venv
source .venv/bin/activate

echo "=== Environment Information ==="
python --version
python -m pip --version
which python
which pip
echo "PATH: $PATH"
echo "PYTHONPATH: $PYTHONPATH"
echo "============================"

echo "=== Upgrading pip ==="
python -m pip install --upgrade pip --no-cache-dir

echo "=== Installing Requirements ==="
pip install -r requirements.txt --no-cache-dir

echo "=== Verifying Gunicorn ==="
.venv/bin/python -m gunicorn --version || echo "Gunicorn missing"

echo "=== Creating Directories ==="
mkdir -p logs

echo "=== Final Environment Check ==="
echo "Python location: $(which python)"
echo "Pip location: $(which pip)"
echo "Gunicorn location: $(which gunicorn || echo 'not found')"
echo "Virtual Environment: $VIRTUAL_ENV"
echo "============================" 