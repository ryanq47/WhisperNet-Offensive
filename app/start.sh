#!/bin/bash



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


echo "start.sh: Loading Configuration Values"
# Load the configuration values from the YAML file
workers=$(yq eval '.wsgi.workers' config/config.yaml)
bind_ip=$(yq eval '.wsgi.bind.ip' config/config.yaml)
bind_port=$(yq eval '.wsgi.bind.port' config/config.yaml)
#tls_country=$(yq eval '.wsgi.bind.port' config/config.yaml)

tls_key=$(yq eval '.server.tls.tls_key_file' config/config.yaml)
tls_crt=$(yq eval '.server.tls.tls_crt_file' config/config.yaml)


generate_ssl() {
    # Note, by default, will overwrite old files. 
    echo "start.sh: Generating TLS certs"
    tls_cn=$(yq eval '.server.tls.tls_cn' config/config.yaml)
    tls_org=$(yq eval '.server.tls.tls_org' config/config.yaml)
    tls_country=$(yq eval '.server.tls.tls_country' config/config.yaml)
    tls_email=$(yq eval '.server.tls.tls_email' config/config.yaml)
    tls_expire=$(yq eval '.server.tls.tls_expire' config/config.yaml)

    openssl req -x509 -nodes -days $tls_expire -newkey rsa:2048 -keyout $tls_key -out $tls_crt -subj "/C=$tls_country/CN=$tls_cn/O=$tls_org/emailAddress=$tls_email"

}

##########
#Main Logic
##########

echo "Checking for TLS Certs"
if [ -e "$tls_key" ]; then
    echo "start.sh: tls private key file exists"
else
    echo "start.sh: The file does not exist, creating..."
    generate_ssl
fi

if [ -e "$tls_crt" ]; then
    echo "start.sh: tls crt file exists"
else
    echo "start.sh: The file does not exist, creating..."
    generate_ssl
fi

echo "start.sh: Starting Gunicorn & Whispernet on $bind_ip:$bind_port"
gunicorn -w $workers 'whispernet:app' --certfile=$tls_crt --keyfile=$tls_key -b $bind_ip:$bind_port 

##openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt


