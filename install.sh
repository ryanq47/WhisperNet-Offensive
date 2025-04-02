#!/bin/bash

# Define colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RESET='\033[0m'

# Detect package manager
if command -v apt-get &>/dev/null; then
    PKG_MANAGER="apt-get"
    UPDATE_CMD="sudo apt-get update"
    INSTALL_CMD="sudo apt-get install -y"
elif command -v dnf &>/dev/null; then
    PKG_MANAGER="dnf"
    UPDATE_CMD="sudo dnf check-update"
    INSTALL_CMD="sudo dnf install -y"
elif command -v pacman &>/dev/null; then
    PKG_MANAGER="pacman"
    UPDATE_CMD="sudo pacman -Sy"
    INSTALL_CMD="sudo pacman -S --noconfirm"
else
    echo -e "${RED}Unsupported package manager. Exiting.${RESET}"
    exit 1
fi

# Function to install a package
install_package() {
    PACKAGE=$1
    echo -e "${CYAN}Installing $PACKAGE...${RESET}"
    if ! command -v "$PACKAGE" &>/dev/null; then
        $INSTALL_CMD "$PACKAGE"
        if command -v "$PACKAGE" &>/dev/null; then
            echo -e "${GREEN}$PACKAGE installed successfully.${RESET}"
        else
            echo -e "${RED}Failed to install $PACKAGE.${RESET}"
            exit 1
        fi
    else
        echo -e "${YELLOW}$PACKAGE is already installed.${RESET}"
    fi
}

# Update package lists
echo -e "${BLUE}Updating package lists...${RESET}"
$UPDATE_CMD

# Install dependencies
install_package "cmake"
install_package "gcc"
install_package "python3"
#install_package "python3-dev"
install_package "nano"

# install docker cuz it's special
echo -e "${CYAN}Installing Docker...${RESET}"
if ! command -v docker &>/dev/null; then
    if [[ "$PKG_MANAGER" == "apt-get" ]]; then
        $INSTALL_CMD docker.io
    elif [[ "$PKG_MANAGER" == "dnf" ]]; then
        $INSTALL_CMD docker
    elif [[ "$PKG_MANAGER" == "pacman" ]]; then
        $INSTALL_CMD docker
    fi

    if command -v docker &>/dev/null; then
        echo -e "${GREEN}Docker installed successfully.${RESET}"
    else
        echo -e "${RED}Failed to install Docker.${RESET}"
        exit 1
    fi
else
    echo -e "${YELLOW}Docker is already installed.${RESET}"
fi

# Add current user to the docker group
echo -e "${CYAN}Adding user to the docker group...${RESET}"
sudo usermod -aG docker "$USER"

# Refresh group membership without logging out
echo -e "${CYAN}Refreshing group membership...${RESET}"
newgrp docker <<EOF
EOF

# Verify docker access
if docker ps &>/dev/null; then
    echo -e "${GREEN}User successfully added to Docker group and Docker is accessible.${RESET}"
else
    echo -e "${YELLOW}You might need to log out and log back in to apply Docker permissions.${RESET}"
fi


# Ensure Docker service is enabled and running
echo -e "${CYAN}Ensuring Docker is running...${RESET}"
sudo systemctl enable docker
sudo systemctl start docker
echo -e "${GREEN}Docker is active.${RESET}"

# Install virtualenv if not installed
echo -e "${CYAN}Checking for virtualenv...${RESET}"
if ! python3 -m venv --help &>/dev/null; then
    echo -e "${YELLOW}Installing virtualenv...${RESET}"
    pip3 install --user virtualenv
fi

# Create virtual environment
VENV_DIR="whispernet_venv"
echo -e "${CYAN}Setting up virtual environment in $VENV_DIR...${RESET}"
python3 -m venv "$VENV_DIR"
echo -e "${GREEN}Virtual environment created at ./$VENV_DIR${RESET}"

# Activate virtual environment and install requirements
echo -e "${CYAN}Activating virtual environment and installing dependencies...${RESET}"
source "$VENV_DIR/bin/activate"
if [[ -f "requirements.txt" ]]; then
	# have to use python in venv, which should just be `python`
    python -m pip install -r requirements.txt
    echo -e "${GREEN}Dependencies installed from requirements.txt.${RESET}"
else
    echo -e "${YELLOW}No requirements.txt found. Skipping...${RESET}"
fi

echo -e "${CYAN} Creating .env...${RESET}"
cp ./Server/app/env_example ./Server/app/.env

nano ./Server/app/.env

# Done
echo -e "${GREEN}Installation complete.${RESET}"

echo -e "============================================================"
echo -e "Cewl - run source ./whispernet_venv/bin/activate to enter the venv"
echo -e "Then, start the server: cd Server && python app/whispernet.py"
echo -e "Finally, spin up the WebGui: cd Web && python main.py --api-host http://<IP_OF_SERVER>:<PORT_OF_SERVER>"
echo -e "You may need to log out, then log back in, and run the above commands again if you get docker permission errors"
echo -e "Also, if you get a 'localhost:6379 : (104, 'Connection reset by peer')' error, re-run python app/whispernet.py, it should fix it"
echo -e "============================================================"
