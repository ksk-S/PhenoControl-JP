#!/bin/bash

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Error: python3 is not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null
then
    echo "Error: pip is not installed."
    exit 1
fi

# Create a virtual environment
if ! python3 -m venv venv
then
    echo "Error: Failed to create a virtual environment."
    exit 1
fi

# Activate the virtual environment
source venv/bin/activate

# Install requirements
if ! pip install -r requirements.txt
then
    echo "Error: Failed to install required packages."
    exit 1
fi

echo "Setup completed successfully."
