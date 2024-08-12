# User Auth

#### Goals:
RBAC if possible
optional 2fa if possible


#### Todo:
- [X] user register function
- [X - Review] User Login function ( creates token )
- [ ] User logout function (invalidates token)
- [ ] Login tracking/Token tracking w DB


- [ ] look into 2fa/auth options?


#### DB Stuff

Primary Key:
 - `id`: A unique id (UUID) is created for each user when registering. This should not ever change. A User's ID is used as the identity portion of the JWT

Unique Keys:
 - `username`. Not primary key, so it can be changed if necessary (change not implemented). Authentication is checked against the username, not the ID.
