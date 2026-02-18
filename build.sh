#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run database migrations (creates session tables, etc.)
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput
