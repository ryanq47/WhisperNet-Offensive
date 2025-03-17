

# <img src="WebInterface/static/icon_full.png" alt="WhisperNet C2 Server" width="100" height="100"> WhisperNet - C2 Framework

Welcome to the WhisperNet C2 server! This project is currently in active development, and features, functionalities, and APIs may change. Please check back regularly for updates! 

---


# **Capabilities**

## The Agent:

### **Windows API Calls (whisper_winapi.h)**
Custom Windows API function wrappers designed for stealthy execution. These calls are engineered to bypass common detection mechanisms and provide near drop-in replacement functionality.

- **Dynamic Function Resolution**  
  - Unhooks the IAT (Import Address Table) by resolving function addresses dynamically via `GetProcAddress`.  
  - Mitigates function call logging via direct `windows.h` references, reducing footprint in IAT-based detections.  
  - Enhances stealth by avoiding static imports that EDRs commonly monitor.

- **Dynamic Function Lookups**  
  - Retrieves function pointers on demand instead of relying on standard linking.  
  - Prevents static analysis detections tied to well-known API calls.  
  - Enables function resolution only when needed, minimizing exposure.

- **(Planned) Standalone `whisper_winapi.h` version**  
  - Provides a true drop-in replacement for existing API calls.  
  - Makes writing your malware easier

### **Whisper Config (whisper_config.h)**


### **Encryption (whisper_config.h)**
 - XOR:
	 - XOR'd Function Calls: Function names are XOR'd at compile time when resolving functions (Ex Key: 0x10):
		 - `resolve("kernel32.dll","VirtualAllocEx");` > `resolve("kernel32.dll","Fybdeq|Q||sUh");`
		 - Why?: Keeps static string detections to a minimum as the plaintext strings are not included in the binary


---

### **Agent Build Features**

#### **CMake/Modular-Based Agents**
WhisperAgents use Cmake based build systems, which just makes **everything** sooooo much easier. 

- Eliminates annoying compile-time issues.
- Ensures clean, structured, and repeatable builds.
- Supports easy cross-compilation for multi-platform deployment.
- Enhances modularity, allowing rapid customization and extension - aka create your own agent.

#### **Custom Configuration Scripts**
- Write your own _per-agent_ python customization scripts
    - Modify existing agents by modifying these scripts
- Select these scripts at agent build time for easy/repeatable customization
- It's just Python, so you can do quite literally whatever you want in these scripts. 

#### **Manual Build Script**
- Backup compile options incase the server decides to break.
- Supports cross-compilation for multi-platform agent deployment.

#### **Agent Template**
- Designed for easy creation of agents

#### **Deployment Options**
| Agent Type/Name             | Executable/Output Formats                                   |  Notes | Running|
|--------------------------------|------------------------------------------------------|-----------|-----------|
|Standard Agent| **.EXE**      | Bog standard EXE agent      | Command: `.\agent.exe` |
|Standard Agent| **.DLL**        |. Same as EXE agent, but in DLL form | Entry Point Function: `Start`<br> Command: `rundll32.exe agent.dll, Start`|

---

## **Operational Security (OPSEC) Considerations**

Opsec features for the Agents. They may vary between agent types, see the `Supported By...` for which agents support which features. 

| Feature                        | OPSEC Benefit                                         | Supported By... | Notes |
|--------------------------------|------------------------------------------------------|-----------|-----------|
| **Dynamic API Resolution**      | Bypasses IAT-based hooks and detection methods      | - Standard Agent (DLL, EXE) <br> - ... |... |


---

## The (Web) Interface

The web interface was made to be easy to use.

### Agents View: All the agents that are actively checking in:
![agents_ss](https://github.com/user-attachments/assets/7786d4ba-9ba4-44db-b3f2-ef0c3cf24eea)


### MultiConsole: Send commands to multiple, or ALL agents at once:
![multi_console_ss](https://github.com/user-attachments/assets/a3e85bd7-b44c-492d-9d56-9e263c73ab56)

### Listeners: All the current listeners:
![listeners_ss](https://github.com/user-attachments/assets/cf733f53-f4bc-4b7a-bd3a-e4dcde5a5c4a)

### File Hosting: 
![host_files_ss](https://github.com/user-attachments/assets/42bbcd3b-dd5d-47ee-964d-02887e824d31)


...

## The Standalone Options
---
## `whisper_winapi.h`

An all in one, drop in header to make stealthier windows api calls. 

### Configuring: 

Before dropping it in, you do need to run a configure script:
```
python3 whisper_winapi_configure.py -f whisper_winapi.h
```

This will adjust some things in the header file, and at this point, it is good to go. 

### Calling a function:

Just append the windows function name, with `whisper`, ex:

```
Sleep(1000);

WhisperSleep(1000);

```

These functions accept the **same arguments** and produce **identical outputs** as their native Windows counterparts, allowing seamless integration. You can refer to the **official Microsoft documentation** for usage guidance.


Current list of implemented functions:

Table?
| Function Name | Desc | MSFT Link | Notes |
|--------------------------------|------------------------------------------------------|-----------|-----|
| **Whisper...**      | Bypasses IAT-based hooks and detection methods      | ...  |... |


## Misc


## **What It Does**
- **Covert Remote Administration** – Issue commands and control remote systems with stealth.
- **Stealthy Execution** – Dynamic function resolution reduces detection footprint.
- **Flexible Deployment** – Modular design allows customization for different operations.
- **Customizable Network Communications** – Avoids default C2 signatures by using non-standard protocols.
- **Red Team Focused** – Built for adversarial simulations and OPSEC-sensitive engagements.

---

