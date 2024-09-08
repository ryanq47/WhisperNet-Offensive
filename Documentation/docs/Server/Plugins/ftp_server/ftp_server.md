# FTP Server Plugin

An FTP server plugin

## Features:

- TLS
    - Automated cert generation
- Anonymous User
- Authenticated Users

## Usage

## TODO:
- [X] add to stats plugin for loaded plugins 
    [X] use ActiveService template
    [X] jwt it
    [X] web client setup of this
    [X] Web clinet endpoint for plugins, 
        and if they have start/stop capabilites, buttons for that

- [X] SSL/TLS + Creation
    - it wants .pem - sooo find a way to handle that/create those certs automatically? Could do a bash script that creates certs for each plugin that needs it, pulls from config file for options? who knows. Also may need a certs directory, orjust store them int eh plugin dorectory ( <<this is prolly easiest)
    or do it in code numnutz

    done in code. auto done if not presetn, all settings in config.yaml

- [X] Perms on user creation?

- [ ] Rearrange/finish filling out this doc

after...
- [ ] FTP client on rust agent

## TLS:

TLS is offered via PyFTPLib's `TLS_FTPHandler`.


#### Certs:
You can generate your own certs if you'd like, but if not, the plugin will generate them for you. It pulls values from config.yaml, in the `server.tls` keys.

The generated files (`ftp_key.pem`,   `ftp_cert.pem`) are then stored at the `plugins/ftp_server/X` directory

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