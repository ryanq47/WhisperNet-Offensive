Below is an updated version of the documentation that explains the **new Python-based command script style** while still keeping it high-level and user-friendly.

---

# **Command Extension Modules**

WhisperNet now supports extending commands using **Python-based modules** rather than a YAML-only scripting approach. This change allows you to leverage full Python capabilities, making your command definitions more modular and dynamic.

Think of it as an **object-oriented macro system**—you define each command as a Python class that inherits from a core `BaseCommand`, and WhisperNet handles command execution by instantiating and running these classes.

**Dev Note**: This approach was introduced to provide greater flexibility and control over command behavior while still maintaining a minimal set of core commands within the agent. It lets you extend and modify behavior on-the-fly without needing to hardcode every command into the agent.

---

## **Example Python Command Module**

Below is an example of a command module using the new format. In this example, a command called `PingHost` is defined to ping a target host. Each command module is a self-contained Python file that implements the required interface:

```python
from modules.agent_script_interpreter import BaseCommand
from modules.agent import BaseAgent

class PingHost(BaseCommand):
    command_name = "ping_host"
    command_help = "Pings a host. Usage: `ping_host <host ip/hostname>`"

    def __init__(self, command, args_list, agent_id):
        """
        command: The command string, e.g. "ping_host"
        args_list: The list of arguments which the user enters,
                   for example: if the user types `ping_host 127.0.0.1`, then args_list = ["127.0.0.1"]
        agent_id: The agent ID on which this command will operate
        """
        super().__init__(command, args_list, agent_id)
        if not command:
            raise ValueError("Missing command")
        if not args_list:
            raise ValueError("Missing args_list")
        if not agent_id:
            raise ValueError("Missing agent_id")

        # Extract the target host from the arguments
        self.host = args_list[0]

        # Initialize a BaseAgent instance to interact with the agent
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        # Optionally call a base method to introduce delays
        # self.set_sleep(2)

        # Build the ping command
        cmd = f"shell ping {self.host}"

        # Enqueue the command to be executed by the agent (returns a command ID)
        shell_cmd_id = self.agent_class.enqueue_command(cmd)

        # Retrieve the command response from the agent (may need a wait or poll)
        shell_cmd_response = (self.agent_class.get_one_command_and_response(shell_cmd_id)
                              or {}).get("response", None)

        # Example logic: if the response indicates a successful ping, do additional processing
        if shell_cmd_response and "Reply from 127.0.0.1" in shell_cmd_response:
            print("Successful Execution")
            # Append extra info to the response and update the agent's command record
            shell_cmd_response += "\n\nTesting Adding onto command, etc"
            self.agent_class.store_response(shell_cmd_id, shell_cmd_response)
```

---

## **How It Works**

1. **Command Definition**  
   Each command is defined as a Python class that inherits from `BaseCommand`. This class must include the attributes `command_name` (used for registration and lookup) and `command_help` (providing usage details).

2. **Dynamic Loading**  
   Command modules are dynamically imported from the filesystem. A loader (or command factory) scans your command directory, registers any class that extends `BaseCommand`, and indexes it by its `command_name`.

3. **Command Execution**  
   When a user issues a command (for example, `ping_host 127.0.0.1`), the agent:
   - Splits the input into the command (`ping_host`) and its arguments (`["127.0.0.1"]`).
   - Looks up the corresponding command class.
   - Instantiates the class with the provided command, arguments, and the agent ID.
   - Calls its `run()` method to execute the command.

4. **Real-Time Flexibility**  
   You can modify or add new commands by simply updating or adding new Python files in your command directory. No agent restart is necessary—commands are discovered and loaded dynamically.

---

## **Operational & OPSEC Considerations**

- **Instant Updates:**  
  Modifying or adding new command modules takes effect immediately on the next command execution.

- **Granular Control:**  
  Each command is self-contained, allowing for detailed logging, debugging, and even dynamic modification before or after execution.

- **Enhanced OPSEC:**  
  With each step executed individually and handled by dedicated classes, you gain better visibility and control over the operations performed by the agent.

---

## **Why Use This Approach?**

- 🚀 **Faster Development Cycle:**  
  Easily write and test new commands using standard Python without extensive configuration.

- ⚡ **Dynamic Extensibility:**  
  Add, modify, or remove commands on the fly—ideal for evolving operational requirements.

- 🔧 **Modular & Maintainable:**  
  Each command is encapsulated in its own module, making the overall system easier to maintain and update.

- 🔒 **Improved Operational Security:**  
  Detailed control over each command's execution flow helps you fine-tune your OPSEC measures.

---

This updated Python-based command script style makes command execution in WhisperNet more structured, flexible, and secure, ensuring that your operations remain dynamic and adaptable to changing needs.