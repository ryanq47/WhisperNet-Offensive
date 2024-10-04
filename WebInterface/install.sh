#!/bin/bash

# Check if the script is sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: This script must be run using 'source', ex 'source install.sh'"
    echo "Usage: source $0"
    exit 1
fi

# Check if venv is available
if ! python3 -m venv --help > /dev/null 2>&1; then
    echo "Error: 'venv' module is not available. Please ensure Python 3 is installed."
    exit 1
fi

# Define the virtual environment name
VENV_NAME="webint_venv"

# Create the virtual environment if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment '$VENV_NAME'..."
    python3 -m venv "$VENV_NAME" || { echo "Failed to create virtual environment."; exit 1; }
else
    echo "Virtual environment '$VENV_NAME' already exists."
fi

# Activate the virtual environment
source "$VENV_NAME/bin/activate"

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing pip requirements..."
    pip install -r requirements.txt || { echo "Failed to install requirements."; exit 1; }
else
    echo "Error: requirements.txt not found."
    exit 1
fi

echo "SUCCESS... hopefully - Anyways, you should be in the 'webint_venv' virtual enviornment. Run 'python3 main.py' to start the server "