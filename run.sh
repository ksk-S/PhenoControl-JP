#!/bin/bash

# Check if port number is provided from environment variable, default to 8080
PORT=${FLASK_PORT:-8080}

PID_FILE="app.${PORT}.pid"

# Activate the virtual environment
if source /home/ec2-user/PhenoControl-JP/venv/bin/activate; then
    echo "Virtual environment activated."
else
    echo "Error: Failed to activate virtual environment."
    exit 1
fi

# Set PYTHONUNBUFFERED to disable buffering
export PYTHONUNBUFFERED=1

# Run the application and create a PID file
python /home/ec2-user/PhenoControl-JP/app.py --port=$PORT &
echo $! > $PID_FILE

# Wait for the application to finish
wait $!

# Deactivate the virtual environment
deactivate

# Clean up the PID file
rm -f $PID_FILE
