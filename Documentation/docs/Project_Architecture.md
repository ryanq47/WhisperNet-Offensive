# Project Architecture

## Technologies & Languages

Something Something Technologies used by whispernet/overview

### Python

### Rust

### Bash


### Redis





## Web Interface

## Server
`app` - DIR: The directory that holds all the components for the Server

- `config` - DIR: Holds the config files


- `instance` - DIR: Holds databases, and database models


- `modules` - DIR: Holds modules, which are non-flexible, and non-routable components of the application


- `plugins` - DIR: Holds plugins, which are used to enhance the functionality of the app. Plugins *have* routable endpoints.
    What is a plugin? A plugin is a single python file that adds extensibilty to the app

