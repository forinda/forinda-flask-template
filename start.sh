#!/bin/bash

# Set Flask environment variables
export FLASK_APP=main.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start Flask application with pipenv
pipenv run flask run --host=0.0.0.0 --port=8000