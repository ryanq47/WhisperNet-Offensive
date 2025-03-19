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
install_package "docker.io"
install_package "python3"
install_package "nano"

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
    pip install -r requirements.txt
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
echo -e "Cewl - run source ./venv/bin/activate to enter the venv"
echo -e "Then, start the server: cd Server && python3 app/whispernet.py"
echo -e "Finally, spin up the WebGui: cd Web && python3 main.py"
echo -e "============================================================"