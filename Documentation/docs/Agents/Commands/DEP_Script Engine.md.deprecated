# Script Engine
---
The **Script Engine** is the magic behind the dynamic loading and interpretation of agent scripts within WhisperNet, allowing you to create, modify, and execute custom commands on the fly without restarting or recompiling.


## Dictionary/Definitons:
---
- Agent Script: The scripts in `Server/data/scripts`, which hold custom commands for the Agents
- Agent builtin commands: The commands harcoded into the Agent binary. Example: `shell`, or `messagebox`

## Scripting Example:
---
For reference, here is an advanced example command that can go into an agent script.

```
######################################
# System Recon (Multi-step)
######################################
class SystemRecon(BaseCommand):
     command_name = "system_recon"
     command_help = (
          "\tUsage: `system_recon` [exfiltration_url] [temp_filepath]\n"
          "\tAggregates system information and network connections.\n"
     )

     def __init__(self, command, args_list, agent_id):
          super().__init__(command, args_list, agent_id)
          self.agent_class = BaseAgent(agent_id)

          self.command_ids = []

     def run(self):
          # dict of commands to run, and store location
          cmds = {
               "shell ver": "system.os",
               "shell whoami": "system.username",
               "shell hostname": "system.hostname",
               "shell powershell -c \"(Get-NetIPAddress -AddressFamily IPv4 | Select-Object -ExpandProperty IPAddress) -join ', '\"": "network.internal_ip",
               'shell powershell -c "(Get-WmiObject Win32_ComputerSystem).Domain"': "network.domain",
               'shell powershell -c "(Get-NetIPConfiguration | Where-Object IPv4DefaultGateway).IPv4DefaultGateway.NextHop"': "network.external_ip",
          }

          # iterating over the dict to get the commands
          for cmd, location in cmds.items():
               # where to store the command on callback
               self.agent_class.store_command_response_on_callback(cmd, location)
               # get each ID
               command_ids = self.agent_class.enqueue_command(cmd)
               # and append command ID's for use elsewhere if needed
               self.command_ids.append(command_ids)
```

## High Level Flow:
---
When you click "send command" while a script is loaded, an inbound command (e.g., "shell whoami") is passed to the script engine. The engine then determines if the command should be handled within the script (by a custom command class) or fall through to the agent’s built-in command queue. The process is non-blocking—it runs in a background thread, so the main thread stays free.

```
                      ┌─────────────────────────────────────┐
                      │ Inbound Command (string), e.g.      │
                      │ "system_recon"                      │
                      └────────────────────┬────────────────┘
                                          │
                                          │ (1) Called by external code
                                          ▼
                      ┌─────────────────────────────────────┐
                      │ AgentScriptInterpreter.__init__()   │ # see Loading From Scripts below to overview this process
                      │ - Init, see "Loading From Scripts"  │
                      └────────────────────┬────────────────┘
                                          │
                                          │ 
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│ MODULE: modules.agent_script_interpreter.py                                  │
│ AgentScriptInterpreter.process_command(inbound_command)                      │
│-----------------------------------------------------------------------------│
│ • Submits self._process_command(...) to a ThreadPoolExecutor                │
│ • Returns a Future immediately (non-blocking)                               │
└───────────────────────┬───────────────────────────────────────────────────────┘
                        │
                        │ (Runs on background, so script execution won't block the main thread)
                        ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│ AgentScriptInterpreter._process_command(inbound_command)                    │
│-----------------------------------------------------------------------------│
│ (a) Logs "Processing command..."                                            │
│ (b) Splits inbound_command → command, args_list (if any args)               │
│ (c) Calls command_factory.create_command(...), which checks if this command │
│     is defined in the loaded agent script                                   │
│ (d) If found, creates and runs the custom command class; if not found,      │
│     falls through to normal agent commands                                  │
│ (e) Returns the result (e.g., a list of queued command IDs)                 │
└───────────────────────┬───────────────────────────────────────────────────────┘
                        │ If command is in the script...
                        │ Command class Lookup and instantiation
                        ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│ CommandFactory.create_command(command_name, args_list, agent_id)            │
│-----------------------------------------------------------------------------│
│ • Looks up command_name in self.commands,                                   |
|     • self.commands is a dict of all commands & its Class Name in the script|
│ • Instantiates the matching subclass of BaseCommand                         │
│ • Returns the new command instance                                          │
└───────────────────────┬───────────────────────────────────────────────────────┘
                        │
                        │ Once the class instance is created, the .run() of said instance is called
                        ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│ <Subclass of BaseCommand> (e.g. PingCommand)                                │
│-----------------------------------------------------------------------------│
│ run():                                                                      │
│   • Performs the actual work (e.g., network call, queueing tasks, etc.)     │
│   • May optionally use self.set_sleep(...) to introduce a delay             │
│   • Returns a list of command IDs (or other result)                         │
└───────────────────────────────────────────────────────────────────────────────┘

               * * * Meanwhile, the main thread remains unblocked * * *
```

## Loading from Scripts & Init:

This is how the scripting engine loads each command from the script file:

```
             ┌─────────────────────────────────────────┐
             │ 1) Instantiate AgentScriptInterpreter   │
             │    with (script_name, agent_id).        │
             └──────────────────────────────┬───────────┘
                                            │
                                            │
                                            ▼
┌───────────────────────────────────────────────────────────────────────┐
│ AgentScriptInterpreter.__init__(script_name, agent_id)              │
│---------------------------------------------------------------------│
│ (a) Validates script_name and agent_id are not blank                │
│ (b) Builds the full path using Config().root_project_path + /data/..│
│ (c) Uses importlib to dynamically load the script file → `module`   │
│ (d) Creates a CommandFactory                                        │
│ (e) Calls command_factory.register_commands_from_module(module)      │
└───────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌───────────────────────────────────────────────────────────────────────┐
│ CommandFactory.register_commands_from_module(module)                 │
│---------------------------------------------------------------------│
│ • Scans the module for classes that inherit from BaseCommand         │
│ • Checks for a command_name attribute on each subclass               │
│ • Stores them in self.commands[command_name]                         │
└───────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│ The script is now "loaded"; custom commands are registered.          │
│ Any inbound command that matches these registered commands           │
│ will create the corresponding BaseCommand subclass.                  │
└───────────────────────────────────────────────────────────────────────┘

```

## FAQ:
---
#### If a command name is both in the script and also a built-in agent command, specify which one actually executes (e.g., does the script override built-in commands or vice versa?):

- The command in the script will be the one queued. It is processed first, and as such, will never directly reach the agent. As such, if you'd like to overload the builtin agent commands (ex, replace `shell`, with your own shell implementation using the builtin commands), go for it. 

#### What if my script has an error or fails to load?

 - If there’s an import or syntax error, *none* of the commands in the script will be registered. In that case, The builtin agent commands still work, but anything in the script won’t be available until you fix the issue.

#### How do I view or verify which commands were successfully registered?
 - Run the `help` command, below the builtin commands, the Script commands should show on screen. If for some reason they do not, either the script has an error, or no script is selected.