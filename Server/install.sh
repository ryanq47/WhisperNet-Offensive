#!/bin/bash

#sudo apt-get install pip -y

echo "Creating virtual environment 'server_venv'..."
python3 -m venv server_venv

# Activate the virtual environment
source server_venv/bin/activate

echo "installing pip reqs"
pip install -r requirements.txt

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

echo "Installing GUnicorn"
sudo apt-get install gunicorn

echo "Pulling & starting redis docker container"
sudo docker run -d --name redis-stack-server -p 6379:6379 redis/redis-stack-server:latest 