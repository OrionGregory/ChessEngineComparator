#!/bin/sh

# Initialize the migrations folder if it doesn't exist
if [ ! -d "/app/migrations" ]; then
  flask db init
fi

# Run database migrations
flask db upgrade

# Start the Flask application
flask run --host=0.0.0.0 --port=5000 --cert=/app/cert.pem --key=/app/key.pem