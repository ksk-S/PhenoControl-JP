#!/bin/bash

# Check if port number is provided, default to 8080
if [ -n "$1" ]; then
  PORT=$1
else
  PORT=8080
fi

# Activate the virtual environment
if source venv/bin/activate; then
    echo "Virtual environment activated."
else
    echo "Error: Failed to activate virtual environment."
    exit 1
fi

# Function to run the application
run_app() {
  python app.py --port=$PORT
}

# Run the application in the background
run_app & echo $! > "app.${PORT}.pid"
echo "Application started successfully on port $PORT."

# Deactivate the virtual environment
deactivate
