# Agents

## Overview
WhisperNet agents are the core components responsible for executing commands, retrieving data, and maintaining remote access to target systems. Unlike traditional RATs (Remote Access Trojans), WhisperNet agents emphasize modularity, stealth, and operational security.

## Types of Agents
WhisperNet supports multiple agent types, each tailored for different operational needs.

| Agent Type       | Format  | Execution Method                               | Notes |
|------------------|---------|-----------------------------------------------|-------|
| Standard Agent   | `.EXE`  | `agent.exe`                                   | Standalone execution |
| DLL Agent       | `.DLL`  | `rundll32 agent.dll, Start`                   | Loadable via `rundll32` |
| Custom Agent    | `.EXE/.DLL` | Varies per configuration                    | Fully customizable/built it yourself |


## Building Agents
### Modular CMake-Based System
WhisperNet agents leverage a CMake-based build system, ensuring:

- **Cross-Platform Support**: Easily compile agents for Windows, Linux, and other platforms.
- **Extensibility**: Modify core behavior without changing the foundational codebase.
- **Reproducibility**: Consistent, structured builds for deployment.

Luckily, the server handles most of the building for you, but the option is there (CMAKE) to do it manually if you'd like. See [Manual Builds](### Manual Agent Building)

### Web Interface

The web interface allows for an automated/easier build options that doing it all manually.

![Binary Build Dialog](../img/webinterface/build_agent_dialog.png)


### Custom Configuration Scripts
Agents can be tailored at build-time using Python scripts:

![Binary Build Dialog](../img/webinterface/build_agent_scripts_dialog.png)

### Manual Agent Building

If you are feeling brave/the web interface isn't working, you can build the agents manually. This is where the CMake magic happens. 

Step 1: Make a copy of the Agent you'd like to build

- `cp -r exe_x64 exe_x64_manual`

Step 2: CD into the newly created directory, and run a configure script on the agent

- `python3 configure.py`

Step 3: Make a "build" directory within the agent directory, and CD into that directory

- `mkdir ./build && cd ./build`

Step 4: Run CMake Configure

- `cmake ..`

Step 5: Build

- `cmake --build .`

Step 6: If all has gone well, you'll find the compiled binary at: `exe_x64_manual/build/bin/someagentname.exe`


Alternatively, this is doable manually as well. It is highly recommended to make a copy of the agent folder instead of working directly on the agent template itself.

Scripts are located in each agent's directory, under the "scripts" folder. 

```bash
cp ./scripts/my_configure_script.py ./configure.py
python3 configure.py
```

## Deployment Considerations
- **Stealth Features**: Implements techniques such as dynamic API resolution and in-memory execution.
- **Execution Methods**: Supports various loading techniques for different operational scenarios.
- **Persistence Options**: Agents can be configured for temporary or persistent deployments.

## Security & OPSEC
- **Signature Avoidance**: Modular builds and obfuscation reduce detection risks.
- **Minimal Network Footprint**: Reduces potential indicators of compromise (IoCs).
- **Encrypted Communications**: Ensures secure transmission between agents and C2 server.

