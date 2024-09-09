# Project Architecture & Technology

## Technologies & Languages

Something Something Technologies used by whispernet/overview

### Python
---

Python is the primary langauge used in this project. The entire server, and web interface are written in it.

### Rust
---

Rust is primarily used by the RAT's/Client. Originally I was planning on writing the client in python, then compile with nuikta, but it turns out cross compilation is a PITA... so a nice (naturally) compiled language ended up being the better candidate. 

### Bash
---

Bash is used for a few scripts here and there, such as the `start.sh` for the server. You'll find it littered throguhout the project for specific things. 

### Redis
---

Redis is used as a shared medium for data. Anything that may need fast & temporary storage will be stored in Redis. In past iterations, a singleton within python was used for this purpose, but singletons and Gunicorn have a potential to not play nice. (TLDR: Changing singleton data + threads on different Gunicorn workers is more of a hassle than just learning Redis) 


### Gunicorn
---

Gunicorn is the WSGI server for the server. It handles a lot of things such as load balancing, and TLS/SSL


## Web Interface

## Server
`app` - DIR: The directory that holds all the components for the Server

- `config` - DIR: Holds the config files


- `instance` - DIR: Holds databases, and database models


- `modules` - DIR: Holds modules, which are non-flexible, and non-routable components of the application


- `plugins` - DIR: Holds plugins, which are used to enhance the functionality of the app. Plugins *have* routable endpoints.

