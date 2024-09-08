# Quick Start

Alright lets get it up and rolling asap.


1. Install reqs:
`pip install -r requirements.txt`

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




4. Make `start.sh` executable, and execute it, everything should start up! Next, check out `<put_a_link_to_webint_quickstart>`

