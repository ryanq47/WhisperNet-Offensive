# FTP Server Plugin

## Features:
- TLS Support
- Automated Certificate Generation
- Anonymous User Access
- Authenticated User Access

### Current Limitations:
The FTP server currently operates as a single data "pool." This means that all users, including `anonymous`, access the same data. Be cautious when enabling anonymous access.

---

## Technical Details

### TLS:
TLS is handled by PyFTPLib's `TLS_FTPHandler`.

#### Certificates:
You can generate your own certificates, but the plugin will automatically generate them if you don't. It pulls configuration values from `config.yaml`, specifically from the `server.tls` keys.  
The generated certificate files (`ftp_key.pem` and `ftp_cert.pem`) are stored in the `plugins/ftp_server/X` directory.

### Redis Keys:
Upon starting the service, a key is added to the Redis database. The key follows the model defined in `modules.redis_models` and contains the following information:

- `sid`: A UUID4 representing the service ID.
- `port`: The port the service is running on.
- `ip`: The IP or DNS name the service is running on.
- `info`: Additional information about the service.
- `timestamp`: The time the service started.

When the service stops, this key is deleted.

---

## API Endpoints:

### `/ftp/new-user`
Adds a new user to the FTP server.

**Schema**:
```json
{
    "username": "",
    "password": ""
}
```

**Note**: This endpoint breaks FormJ formatting.

---

### `/ftp/start`
Starts the FTP server.

---

### `/ftp/stop`
Stops the FTP server.

---

## Users

### Anonymous User:
The `anonymous` user only has write access if explicitly enabled (a setting for this can be added).  
This is intended for easy exfiltration over FTP without needing credentials.

---

### Authenticated Users:
You can add authenticated users to the FTP server via the `/ftp/new-user` endpoint. At the moment this is not doable via the web interface.

---

