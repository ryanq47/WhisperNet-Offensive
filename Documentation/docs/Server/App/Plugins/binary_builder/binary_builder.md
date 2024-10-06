# Binary Builder Server Plugin

The binary builder plugin is used for building binaries, in docker. 

## Features:
 - Docker handler
 - Rust Compliation

### Current Limitations:

---

## Technical Details

### Important file paths:

 - `./_docker/`: The main "docker" folder. This contains the leading `_` to not conflict with the `docker` python library
    - `dockerfiles`: Holds the docker files for building the containers

 - `./data`: Data folder for holding anything data
    - `compiled`: Where all compiled binaries will be stored. Docker outputs them to this folder. 

### Dockerfile files
The dockerfiles are used to build the docker containers. They are named as such: `container-os_target-os_architecture.dockerfile`. For now, the goal is to have a dockerfile for each target-os, and architecture. 

### Targets

Current supported targets:
 - `x64_windows_stageless`


## API Endpoints:

### `/binary_builder/<target>` - POST

Build a compile enviornment, and compile a binary. 




