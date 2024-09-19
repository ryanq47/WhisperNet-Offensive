# Quick Start

Quick start to getting the server up and rolling.



1. Run `install.sh` to install all the needed items
This will install:
    - Redis Docker Container (Also starts it)
    - Requirements.txt
    - Gunicorn
    - yq

2. Config .env
```
cp ./app/env.example ./app/.env
```
Edit new `.env` with your editor of choice:

```
JWT_SECRET_KEY="somejwtkey" # Your secret key for JWT tokens, KEEP THIS STRONG
SECRET_KEY="somekey"        # The general secret key for the flask app, also keep strong

# Initial user credentials that are used if no users exist in DB
DEFAULT_USERNAME="username" # Please change
DEFAULT_PASSWORD="password" # Please Change

```

3. Optional, review `./app/config/config.yaml` for additional server settings/options.


4. Make `app/start.sh` executable, and execute it, everything should start up!

## Troubleshooting:

### Redis errors:

#### Make sure docker container is up/exists:

This will list all docker containers:
```
sudo docker ps -a
```

This will start the docker container:
```
sudo docker start <CONTAINER ID>
``` 

#### If you are in a VM, and suspended the session:

For some reason, Docker networking breaks on my dev box when I suspend it. You can fix that with this command:

```
sudo systemctl restart NetworkManager docker
```

Then, go and restart the Redis container (see above command)
