#!/bin/bash

# Ensure a port number is provided, default to 8080
if [ -n "$1" ]; then
  PORT=$1
else
  PORT=8080
fi

PID_FILE="app.${PORT}.pid"

# Check if PID file exists
if [ -f $PID_FILE ]; then
  PID=$(cat $PID_FILE)
  if kill $PID > /dev/null 2>&1; then
    echo "Application on port $PORT stopped successfully."
    rm $PID_FILE
  else
    echo "Error: Failed to stop application on port $PORT."
    rm $PID_FILE
  fi
else
  echo "Error: PID file for port $PORT not found. Is the application running?"
fi

# Ensure the port is not in use
if lsof -i tcp:$PORT > /dev/null; then
  echo "Port $PORT is still in use. Attempting to free it."
  lsof -t -i tcp:$PORT | xargs kill -9
  if [ $? -eq 0 ]; then
    echo "Port $PORT successfully freed."
  else
    echo "Failed to free port $PORT. Manual intervention may be required."
  fi
else
  echo "Port $PORT is not in use."
fi
