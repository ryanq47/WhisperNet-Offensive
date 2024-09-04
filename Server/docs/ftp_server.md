# FTP Server Plugin

An FTP server plugin

## Usage



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