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

#### Build Options:

##### Agent Name
(Optional) The name of the binary after it is built.

If left blank, the generated format will be:

`RANDOM_NAME_architecture_CallbackAddress_CallbackPort.FileExtension`

I figured this makes it easier to track which agent does what/talks to where.


---

##### Agent Type

The type of agent

| Agent Type/Name             | Executable/Output Formats                                   |  Notes | Running|
|--------------------------------|------------------------------------------------------|-----------|-----------|
|Standard Agent (exe_x64) | **.EXE**      | Bog standard EXE agent      | Command: `.\agent.exe` |
|Standard Agent (dll_x64) | **.DLL**        |. Same as EXE agent, but in DLL form | Entry Point Function: `Start`<br> Command: `rundll32.exe agent.dll, Start`|
---

##### Agent Callback Address

The address the agent will callback too.

Ex: `1.1.1.1`

---

##### Agent Callback Port

The port the agent will callback too.

Ex: `9999`

---


##### Custom Configuration Scripts
The config script used to modify the agent. These are located at `<name_of_agent>/scripts`


| Agent Type/Name             | Script                                |  Short Description | 
|--------------------------------|------------------------------------------------------|-----------|
|Standard Agent (exe_x64) | `default.py`    | The default configure script. XOR's strings, etc.     | 
|Standard Agent (dll_x64) | `default.py`    | The default configure script. XOR's strings, etc.     | 

![Binary Build Dialog](../img/webinterface/build_agent_scripts_dialog.png)

---

### Building the agent

After you've filled in all the relevant details, click `Build Agent`. This will start the build process on the server

After a few seconds, hit the `refresh` button in the bottom right, and you should see the newly built agent!

![Build Agent](../img/webinterface/built_agent.png)

---


# **Manual Agent Building Guide**  
For when you're feeling brave or the web interface isn't cooperating.

---

## **Step 1: Copy the Agent Directory**  
Create a manual copy of the agent you want to build:  

```bash
cp -r exe_x64 exe_x64_manual
```
---

## **Step 2: Run the Configure Script**  
Navigate into the new directory and run the configuration script:  

```bash
cd exe_x64_manual
python3 configure.py
```

This may ask for options, if so, fill them in:
```
└─$ python3 configure.py
WARNING: By nature... these values are injectable. Don't be stupid, stick to the examples.
[REQ] Enter the agent name: MyAgent
[REQ] Enter the callback address (Ex: '1.1.1.1', 'somedomain.com') (do NOT include the '): 1.1.1.1
[REQ] Enter the callback port (Ex: 9999): 9999

```


To use a different script, copy a script from the `scripts` folder, into the agent folder:  
 - *Scripts are located in each agent's `scripts` folder.*  

```bash
cp ./scripts/my_configure_script.py ./configure.py
python3 configure.py
```

NOTE: These are one-shot scripts. Once an agent has been configured with a script, it cannot be re-configued. You will need to re-copy the agent and re-run the script to reconfigure.

---

## **Step 3: Create & Enter the Build Directory**  

```bash
mkdir ./build && cd ./build
```
---

## **Step 4: Run CMake Configure**  

```bash
cmake ..
```
---

## **Step 5: Build the Agent**  

```bash
cmake --build .
```
---

## **Step 6: Locate the Compiled Binary**  
If everything went well, you’ll find the compiled agent here:  

```bash
exe_x64_manual/build/bin/someagentname.exe
```

*Done! Your manually built agent is ready to go.*  
