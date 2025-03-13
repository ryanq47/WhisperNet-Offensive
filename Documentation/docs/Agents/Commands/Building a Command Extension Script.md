# **Building Your Own Python Command Scripts**

HCKD now supports extending commands using **Python modules**. This approach is designed for flexibility and modularity, allowing you to define command sequences using standard Python classes. This section provides a technical deep dive into structuring, executing, and optimizing your own command scripts.

> **Note:** This isn’t a full scripting language—rather, it’s a modular, object‑oriented way to define commands. Each command is implemented as a Python class that inherits from a common base class and implements a standardized interface.

---

## **Python Module Structure Overview**

Each command module is a standalone Python file that contains one or more command classes. Every command class must extend the core `BaseCommand` and define two key attributes:
  
```python
command_name = "<unique_command_identifier>"
command_help = "<brief usage description>"
```

Additionally, each class must implement:
- **`__init__`**: Accepts the command string, an arguments list, and an agent ID.
- **`run()`**: Contains the logic to execute the command.

### **Example: PingHost Command Module**

```python
from modules.agent_script_interpreter import BaseCommand
from modules.agent import BaseAgent

class PingHost(BaseCommand):
    command_name = "ping_host"
    command_help = "Pings a host. Usage: `ping_host <host ip/hostname>`"

    def __init__(self, command, args_list, agent_id):
        """
        command: The command string, e.g. "ping_host"
        args_list: List of arguments provided by the user.
                   For example, if the user types `ping_host 127.0.0.1`,
                   then args_list = ["127.0.0.1"]
        agent_id: The agent identifier to operate on.
        """
        super().__init__(command, args_list, agent_id)
        if not command:
            raise ValueError("Missing command")
        if not args_list:
            raise ValueError("Missing args_list")
        if not agent_id:
            raise ValueError("Missing agent_id")

        # Extract the target host from the arguments.
        self.host = args_list[0]

        # Instantiate BaseAgent to interact with the target agent.
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        # Optionally, invoke a base method to add delays.
        # self.set_sleep(2)

        # Build the ping command.
        cmd = f"shell ping {self.host}"

        # Enqueue the command for execution (returns a command ID).
        shell_cmd_id = self.agent_class.enqueue_command(cmd)

        # Retrieve the command response (may require waiting/polling).
        shell_cmd_response = (self.agent_class.get_one_command_and_response(shell_cmd_id) or {}) \
                                .get("response", None)

        # If a successful reply is detected, process further.
        if shell_cmd_response and "Reply from 127.0.0.1" in shell_cmd_response:
            print("Successful Execution")
            # Append additional details to the response.
            shell_cmd_response += "\n\nTesting Adding onto command, etc"
            self.agent_class.store_response(shell_cmd_id, shell_cmd_response)
```

---

## **Execution Flow**

1. **Dynamic Loading & Registration**

   - A command factory or loader scans your designated directory for Python files.
   - Each module is imported dynamically, and all classes inheriting from `BaseCommand` are registered using their `command_name` attribute.
   - This allows HCKD to discover and execute new command modules without any hardcoded updates.

2. **Command Invocation**

   - The user inputs a command string (e.g., `ping_host 127.0.0.1`).
   - The input is split into the command (`ping_host`) and its arguments (`["127.0.0.1"]`).
   - The factory instantiates the appropriate command class with the command, arguments, and agent ID.
   - The `run()` method of the instantiated command is called to execute the command.

---

## **Dynamic Module Loading Example**

Below is a sample command factory that loads command modules, registers command classes, and creates command instances dynamically:

```python
import importlib.util
import inspect
import os
from modules.agent_script_interpreter import BaseCommand

class CommandFactory:
    def __init__(self):
        self.commands = {}

    def load_command_module(self, module_path):
        if not os.path.exists(module_path):
            raise FileNotFoundError(f"Module not found: {module_path}")
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self._register_commands_from_module(module)

    def _register_commands_from_module(self, module):
        # Iterate over all classes defined in the module.
        for name, cls in inspect.getmembers(module, inspect.isclass):
            # Register subclasses of BaseCommand (ignore BaseCommand itself).
            if issubclass(cls, BaseCommand) and cls is not BaseCommand:
                if hasattr(cls, 'command_name'):
                    command_name = getattr(cls, 'command_name')
                    self.commands[command_name] = cls
                    print(f"Registered command: {command_name}")
                else:
                    print(f"Warning: {name} does not define a command_name attribute")

    def create_command(self, command_name, args, agent_id):
        command_cls = self.commands.get(command_name)
        if command_cls is None:
            raise ValueError(f"Command '{command_name}' is not registered")
        # Instantiate the command with the proper parameters.
        return command_cls(command_name, args, agent_id)
```

---

## **Best Practices for Custom Python Command Scripts**

### **Keep Commands Modular**
- **Separation of Concerns:**  
  Define each command in its own module to keep code maintainable.
- **Granular Functionality:**  
  Break complex operations into smaller, dedicated commands.

### **Error Handling and Logging**
- **Robust Exception Management:**  
  Use Python’s exception handling within your `run()` method to manage errors gracefully.
- **Detailed Logging:**  
  Integrate logging to trace command execution and assist with debugging.

### **Testing and Validation**
- **Unit Testing:**  
  Write tests for individual command modules to ensure expected behavior.
- **Input Validation:**  
  Validate inputs in the `__init__` method to prevent runtime errors.

### **Operational Security (OPSEC)**
- **Sensitive Data:**  
  Be cautious with logging sensitive command outputs.
- **Execution Modes:**  
  Consider using synchronous execution for dependent tasks to ensure commands complete in sequence.

---

## **Integrating Python Command Scripts with the Agent**

With dynamic module loading, HCKD automatically loads your command scripts before each command is executed. This means:

1. **Immediate Application:**  
   Any changes or additions to command modules take effect instantly without restarting the agent.

2. **Dynamic Dispatch:**  
   The agent uses the command factory to look up, instantiate, and execute the correct command based on user input.

3. **Consistent Execution Flow:**  
   Each command follows a standardized flow—from initialization and validation to execution and response handling.

---

## Examples:

### Populate data fields/get some basic info on a host.

```
class Populate(BaseCommand):
    command_name = "populate"
    command_help = "Populates common data fields. Usage: `populate`"

    def __init__(self, command, args_list, agent_id):
        """
        command: The command string, e.g. "populate"
        args_list: List of arguments provided by the user (not used here)
        agent_id: The agent identifier to operate on.
        """
        super().__init__(command, args_list, agent_id)
        if not agent_id:
            raise ValueError("Missing agent_id")
        # Instantiate a BaseAgent to handle command execution.
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        # Enqueue a sleep command (10 seconds) before execution.
        self.agent_class.enqueue_command("sleep 10")
        
        # Execute shell command "ver"
        self.agent_class.enqueue_command("shell ver")
        
        # Execute shell command "whoami"
        self.agent_class.enqueue_command("shell whoami")
        
        # Execute shell command "hostname"
        self.agent_class.enqueue_command("shell hostname")
        
        # Enqueue a sleep command (10 seconds) after execution.
        self.agent_class.enqueue_command("sleep 10")
```