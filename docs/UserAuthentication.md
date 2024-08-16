# User Auth

#### Goals:
RBAC if possible
optional 2fa if possible


#### Todo:
- [X] user register function
- [X - Review] User Login function ( creates token )


- [ ] look into 2fa/auth options?

- [X] Default args for a user/pass if none specified in DB. 
    currently, registration endpoint is open to anyone. Can change this by disabling registrion endpoint through settings, or doing a jwt_required. 

- [ ] Clean up/re-go over code, then merge into main

## Notes:

#### Tokens:
- Expire after 15 minutes, by default. You can change this via the `config.server.authentication.token.expiration` key in the config.yaml


#### Default User:
If the user table is empty, a new user will be created with the credentials in the .env file. Use the env.example to create a `.env` file.