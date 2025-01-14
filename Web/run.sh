#!/bin/bash

# Set variables
VENV_DIR="./venv"
REQUIREMENTS_FILE="requirements.txt"
MAIN_SCRIPT="main.py"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
    echo "Virtual environment created."
else
    echo "Virtual environment found."
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi
echo "Virtual environment activated."

# Install Python requirements
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing Python requirements..."
    pip install -r "$REQUIREMENTS_FILE"
    if [ $? -ne 0 ]; then
        echo "Failed to install Python requirements."
        deactivate
        exit 1
    fi
    echo "Python requirements installed."
else
    echo "Requirements file not found. Skipping installation."
fi

# Run the main script
if [ -f "$MAIN_SCRIPT" ]; then
    echo "Running $MAIN_SCRIPT..."
    python "$MAIN_SCRIPT"
    if [ $? -ne 0 ]; then
        echo "Failed to run $MAIN_SCRIPT."
        deactivate
        exit 1
    fi
else
    echo "$MAIN_SCRIPT not found. Exiting."
    deactivate
    exit 1
fi

# Deactivate the virtual environment
deactivate
