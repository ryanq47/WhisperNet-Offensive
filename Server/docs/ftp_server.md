# FTP Server Plugin

An FTP server plugin

## Usage

## TODO:
- [X] add to stats plugin for loaded plugins 
    [X] use ActiveService template
    [X] jwt it
    [X] web client setup of this
    [X] Web clinet endpoint for plugins, 
        and if they have start/stop capabilites, buttons for that

- [ ] SSL/TLS + Creation
    - it wants .pem - sooo find a way to handle that/create those certs automatically? Could do a bash script that creates certs for each plugin that needs it, pulls from config file for options? who knows. Also may need a certs directory, orjust store them int eh plugin dorectory ( <<this is prolly easiest)
    or do it in code numnutz

- [ ] Perms on user creation?
- [ ] Mini web cleanup + notifications for things


after...
- [ ] FTP client on rust agent

## Redis Keys:

On start, a service key is added to the redis db. 

This key contains the following: (Note, key model can be found at `modules.redis_models`)

`sid`: UUID4, the service ID
`port`: port the service is on
`ip`: ip/dns name service is on
`info`: info about the service
`timestamp`: Timestamp of when the service started

On stop, this key is deleted


## Endpoints:

`/ftp/new-user`

Adds new user to FTP server

Schema - breaks formj
```
{
    username="",
    password=""
}

```

`/ftp/start`

Starts FTP server


`/ftp/stop`

Stops FTP server


## User:

`anonymous`: The anonymous user. Only has write access to server if enabled (add setting for that?). 

This is meant to allow for easy exfil over FTP without entering creds for the FTP server


#### Actual users
So, you can add actual users to this thing as well.

(instructions how to later)

The `/ftp/new-user` endpoint allows to add a new user. These users have `` permissions.

These users are meant to be *actual* ftp users, or if you're feeling daring, a password protected exfil account. 

*Todo: Give default perms, or add a perms field for this endpoint for adding new users*