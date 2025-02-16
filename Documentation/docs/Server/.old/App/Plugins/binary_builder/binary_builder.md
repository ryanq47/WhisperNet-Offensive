Here’s an enhanced version with additional explanations, clearer formatting, and added details for clarity:

---

# Binary Builder Server Plugin

The **Binary Builder Plugin** is designed to streamline the process of building binaries using Docker environments. It leverages Docker for creating isolated compilation environments, particularly for Rust binaries intended for cross-platform support. This setup is ideal for compiling binaries in a repeatable, modular, and scalable manner.

## Features

- **Docker Handler**: Manages Docker containers for isolated compilation environments.
- **Rust Compilation**: Supports cross-compilation of Rust binaries, specifically for Windows targets.

### Current Limitations
- Currently limited to Rust binaries.
- Support for other languages or environments may require additional configuration.

---

## Technical Details

### Important File Paths

- `./_docker/`: The main directory for Docker-related files, prefixed with `_` to avoid conflicts with the `docker` Python library.
  - `dockerfiles`: Directory for Dockerfiles used to build containers, each named according to the target environment (e.g., `debian_windows_x64.dockerfile`).
  
- `./data`: Directory to store output and working data.
  - `compiled`: Folder where all compiled binaries are stored after the build process, allowing easy access to the compiled files. Docker outputs compiled binaries directly into this folder.

### Dockerfile Conventions
Each Dockerfile is uniquely named to indicate the target operating system and architecture. Naming follows the pattern: `container-os_target-os_architecture.dockerfile`. Currently, each target OS and architecture requires a separate Dockerfile to ensure all dependencies are correctly handled.

### Supported Targets

The current plugin supports compiling the following target:
- **x64_windows_stageless**: A binary format optimized for Windows 64-bit without staging.

---

## API Endpoints

Here’s comprehensive documentation for the three endpoints, covering purpose, parameters, example requests, responses, and potential errors.

### Overview
The Binary Builder API provides endpoints for compiling custom binaries, droppers, and agents using Docker containers. Each endpoint uses specific Docker configurations to compile binaries tailored to user-defined specifications.

---

### 1. **`POST /binary-builder/build/custom`**
#### Description
Compiles a custom binary specified by the user with provided target architecture, shellcode, and binary name.

#### Request Parameters
- **Method**: `POST`
- **Content-Type**: `application/json`
- **JSON Payload**:
  - `target` (string, required): The target architecture and OS for the binary. Accepted values include:
    - `"x64_windows_custom"`
    - `"x86_windows_custom"`
  - `shellcode` (string, required): Base64-encoded shellcode to include in the binary.
  - `binary_name` (string, required): Desired name of the output binary file.

#### Example Request
```json
POST /binary-builder/build/custom
Content-Type: application/json

{
  "target": "x64_windows_custom",
  "shellcode": "aabbcc==",
  "binary_name": "custom_binary"
}
```

#### Example Response
```json
{
  "message": "successfully built x64_windows_custom",
  "status": 200
}
```

#### Error Responses
- **400 Bad Request**: Missing fields in the JSON payload.
  ```json
  {
    "message": "Missing fields in request",
    "status": 400
  }
  ```
- **400 Bad Request**: Unknown target.
  ```json
  {
    "message": "Unknown target",
    "status": 400
  }
  ```
- **500 Internal Server Error**: Generic server error during build.
  ```json
  {
    "message": "An error occurred",
    "status": 500
  }
  ```

---

### 2. **`POST /binary-builder/build/dropper`**
#### Description
Builds a dropper binary for the specified target, with options for IP, port, and binary name.

#### Request Parameters
- **Method**: `POST`
- **Content-Type**: `application/json`
- **JSON Payload**:
  - `target` (string, required): Specifies the dropper target environment. Accepted values include:
    - `"x64_windows_dropper"`
    - `"x86_windows_dropper"`
  - `ip` (string, required): IP address for the dropper to use in the generated binary.
  - `port` (string, required): Port for the dropper to connect to.
  - `binary_name` (string, required): Desired name of the output dropper file.

#### Example Request
```json
POST /binary-builder/build/dropper
Content-Type: application/json

{
  "target": "x64_windows_dropper",
  "ip": "192.168.1.100",
  "port": "8080",
  "binary_name": "dropper_binary"
}
```

#### Example Response
```json
{
  "message": "successfully built x64_windows_dropper",
  "status": 200
}
```

#### Error Responses
- **400 Bad Request**: Missing fields in the JSON payload.
  ```json
  {
    "message": "Missing fields in request",
    "status": 400
  }
  ```
- **400 Bad Request**: Unknown target.
  ```json
  {
    "message": "Unknown target",
    "status": 400
  }
  ```
- **500 Internal Server Error**: Generic server error during build.
  ```json
  {
    "message": "An error occurred",
    "status": 500
  }
  ```

---

### 3. **`POST /binary-builder/build/agent`**
#### Description
Builds an agent binary for the specified target, which can be a dropper or custom agent.

#### Request Parameters
- **Method**: `POST`
- **Content-Type**: `application/json`
- **JSON Payload**:
  - `target` (string, required): The target architecture and OS for the agent. Accepted values include:
    - `"x64_windows_agent"`
    - `"x86_windows_agent"`
  - `ip` (string, required): IP address for the agent binary.
  - `port` (string, required): Port for the agent binary.
  - `binary_name` (string, required): Desired name of the output agent file.

#### Example Request
```json
POST /binary-builder/build/agent
Content-Type: application/json

{
  "ip": "192.168.1.100",
  "port": "8080",
  "binary_name": "agent_binary"
}
```

#### Example Response
```json
{
  "message": "successfully built x64_windows_agent",
  "status": 200
}
```

#### Error Responses
- **400 Bad Request**: Missing fields in the JSON payload.
  ```json
  {
    "message": "Missing fields in request",
    "status": 400
  }
  ```
- **400 Bad Request**: Unknown target.
  ```json
  {
    "message": "Unknown target",
    "status": 400
  }
  ```
- **500 Internal Server Error**: Generic server error during build.
  ```json
  {
    "message": "An error occurred",
    "status": 500
  }
  ```

---

### Notes
- **Configuration**: Targets, Dockerfile paths, and build details are defined in the configuration file (`config.yaml`). Each target must be mapped to a Dockerfile, defining compilation environments for different binaries.
- **File Storage**: Compiled binaries are saved in the `/data/compiled` folder, accessible via endpoint calls to serve or retrieve binaries.

---

## Full Compile Workflow

This workflow outlines the complete step-by-step process for compiling a binary through the Binary Builder Plugin:

1. **Configuration Loading**:
   - The configuration file (`config.yaml`) is loaded. This file contains all Docker and binary-specific information needed for the build, such as Dockerfile paths, descriptions, and the target language.

2. **User Request**:
   - The user initiates the build by selecting "Queue for Compilation" or hitting a designated endpoint in the plugin.

   Endpoints that trigger this process:
      - `/binary_builder/build/custom`
      - `/binary_builder/build/agents`
      - `/binary_builder/build/droppers`


3. **Plugin Request Handling**:
   - The plugin receives an HTTP request to the designated endpoint. This request includes target specifications (e.g., `x64_windows_dropper`).

4. **Initiate Build**:
   - The `build` function in the `docker_builder.py` module is called. 
   - This function uses the configurations from the `config.yaml` file to select the appropriate Dockerfile, configure the build context, and set the output directory.

5. **Docker Environment Setup**:
   - The Docker container is built with the specified Dockerfile, establishing the necessary environment for Rust cross-compilation (e.g., installing toolchains, dependencies).
   - The container copies source files (typically located in `agents/`) and compiles them according to build specifications.

6. **Binary Compilation and Output**:
   - After successful compilation, the resulting binaries are output into the `data/compiled` folder, which serves as the central location for all compiled binaries. 
   - Currently, these binaries are accessible through the `binary_builder/?` endpoint, where they can be retrieved or downloaded.

7. **Cleanup**:
   - The container is automatically removed post-build to maintain a clean environment and optimize resource usage.

### Configuration Example

The configuration for each binary target is specified in the `config.yaml` file. Each target includes a buildfile path, description, and language for build instructions:

```yaml
binaries:
   droppers:
      x64_windows_dropper: 
         buildfile: "_docker/dockerfiles/debian_windows_dropper_x64.dockerfile"
         description: "An x64 Windows dropper"
         language: "rust"
```

Each Dockerfile performs several critical steps:
- Sets up the required compilation environment (e.g., Rust toolchains, cross-compilation dependencies).
- Copies the source files from the `agents/` directory into the container.
- Compiles the binary during the build process.
- Outputs the compiled binary to the `data/compiled` directory, where it can be accessed by other components or endpoints.

