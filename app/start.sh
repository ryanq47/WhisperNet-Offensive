
# Ensure yq is installed
if ! command -v yq &> /dev/null
then
    echo "yq could not be found, please install it first"
    exit
fi

echo "start.sh: Loading Configuration Values"
# Load the configuration values from the YAML file
workers=$(yq eval '.wsgi.workers' config/config.yaml)
bind_ip=$(yq eval '.wsgi.bind.ip' config/config.yaml)
bind_port=$(yq eval '.wsgi.bind.port' config/config.yaml)

echo "start.sh: Starting Gunicorn & Whispernet on $bind_ip:$bind_port"
gunicorn -w $workers 'whispernet:app' -b $bind_ip:$bind_port