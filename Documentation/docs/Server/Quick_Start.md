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
`cp ./app/env.example ./app/.env``
```
Edit new .env with your editor of choice:

```
JWT_SECRET_KEY="somejwtkey" # Your secret key for JWT tokens, KEEP THIS STRONG
SECRET_KEY="somekey" # The general secret key for the flask app, also keep strong

#Default creds used if no users exist in DB
DEFAULT_USERNAME="username" # Please change
DEFAULT_PASSWORD="password" # Please Change

```

3. Optional, review `./app/config/config.yaml` for additional server settings/options.


4. Make `app/start.sh` executable, and execute it, everything should start up! Next, check out `<put_a_link_to_webint_quickstart>`

