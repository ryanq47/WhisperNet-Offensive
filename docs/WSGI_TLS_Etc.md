# WSGI, TLS, Etc

Gunicorn is used for the WSGI server.

It is called from app/start.sh, all configuration items are found at `config/config.yaml`

Deps:
 - yq (https://github.com/mikefarah/yq)

## TLS configuration

TLS is handled via Gunicorn. Configuration values can be found in `app/config/config.yaml`, under `server.tls`.

All TLS settings are here. 

```
tls:
# These do not need to exist, however, if they don't, start.sh will create them with the below options
tls_key_file: !!str ./server.key
tls_crt_file: !!str ./server.crt

# common name for tls cert
tls_cn: !!str "some.domain"

# org name for tls cert
tls_org: !!str "some-company"

# country code for tls cert, 2 letters
tls_country: !!str "AA"

# email for tls cert - if you feel like doxing yourself. 
tls_email: !!str "some@email.com"

# How long before the cert expires
tls_expire: !!int 180
```




## Generating self signed certificates
`start.sh` will auto generate the certs (server.key & server.crt) if they do not exist. 

If you want to generate your own, this is the command used:

```
openssl req -x509 -nodes -days 180 -newkey rsa:2048 -keyout server.key -out server.crt
```