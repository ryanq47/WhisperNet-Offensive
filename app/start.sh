#!/bin/bash



# Ensure yq is installed
if ! command -v yq &> /dev/null
then
    echo "start.sh: yq could not be found, installing locally at ~/.local/bin/yq"

    wget https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_linux_amd64 -O yq_linux_amd64 --show-progress
    cp yq_linux_amd64 ~./local/bin/yq # install locally JUST for current user
    rm yq_linux_amd64

    exit
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


