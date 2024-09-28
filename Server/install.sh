#!/bin/bash

# make sure source calls this script
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: This script must be run using 'source', ex 'source install.sh'"
    echo "Usage: source $0"
    exit 1
fi

#sudo apt-get install pip -y

 
# Check if venv is available
if ! python3 -m venv --help > /dev/null 2>&1; then
    echo "Error: 'venv' module is not available. Please ensure Python 3 is installed."
    exit 1
fi


# Define the virtual environment name
VENV_NAME="server_venv"

# Create the virtual environment if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment '$VENV_NAME'..."
    python3 -m venv "$VENV_NAME"
else
    echo "Virtual environment '$VENV_NAME' already exists."
fi

# Activate the virtual environment
source "$VENV_NAME/bin/activate"

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing pip requirements..."
    pip install -r requirements.txt
else
    echo "Error: requirements.txt not found."
    exit 1
fi

# Ensure yq is installed
if ! command -v yq &> /dev/null
then
    echo "start.sh: yq could not be found."

    # Prompt the user for installation
    read -p "start.sh: Do you want to install yq locally at ~/.local/bin/yq? [Y/n]: " answer
    answer=${answer:-Y}  # Default to 'Y' if no input is provided

    if [[ "$answer" =~ ^[Yy]$ ]]; then
        echo "start.sh: Installing yq locally..."

        # Download yq
        wget https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_linux_amd64 -O yq_linux_amd64 --show-progress -nv
        
        # Create directory if it does not exist
        mkdir -p ~/.local/bin

        # Install yq locally
        mv yq_linux_amd64 ~/.local/bin/yq
        chmod +x ~/.local/bin/yq  # Make it executable

        # Clean up
        echo "start.sh: Cleaning up..."
        rm yq_linux_amd64

        echo "start.sh: moving yq to /usr/bin/yq"
        sudo cp ~/.local/bin/yq /usr/bin/yq
        
        echo "start.sh: yq has been installed successfully at ~/.local/bin/yq."

        # Optionally, inform the user to add to PATH if not already
        if ! echo "$PATH" | grep -q "~/.local/bin"; then
            echo "start.sh: Reminder: Ensure ~/.local/bin is in your PATH to use yq easily. \n If not, try 'sudo cp ~/.local/bin/yq /usr/bin/yq' to install for all users"
        fi
    else
        echo "Installation aborted. Cannot continue without yq."
        exit 1
    fi
fi
## make sure docker is installed
if ! command -v docker &> /dev/null
then
    echo "start.sh: docker could not be found."

    # Prompt the user for installation
    read -p "start.sh: Do you want to install yq locally at ~/.local/bin/yq? [Y/n]: " answer
    answer=${answer:-Y}  # Default to 'Y' if no input is provided

    if [[ "$answer" =~ ^[Yy]$ ]]; then
        echo "start.sh: Installing docker..."

        sudo apt-get install docker.io
    else
        echo "Installation aborted. Cannot continue without docker."
        exit 1
    fi
fi


echo "Installing GUnicorn"
sudo apt-get install gunicorn

echo "Pulling & starting redis docker container"
#may need to pull this based on docker in python implementation
sudo docker run -d --name redis-stack-server -p 6379:6379 redis/redis-stack-server:latest 

echo "SUCCESS... hopefully - Anyways, you should be in the 'server_venv' virtual enviornment "