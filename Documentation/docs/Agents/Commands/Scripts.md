# Scripts
WhisperNet’s **Script Engine** provides a flexible, non-blocking way to dynamically load and run custom commands for your agents. By defining special-purpose scripts—complete with their own command classes—you can seamlessly introduce new functionality (from quick checks like “shell whoami” to more advanced recon tasks) without recompiling or restarting anything. At runtime, inbound commands first route through the **script interpreter**, which creates and executes any matching command classes it finds, or else falls back to the agent’s built-in commands. This design allows for on-the-fly updates to script logic, as well as convenient dot-accessible data storage in the **Agent Data Model**—helping you keep track of important info in Redis and display it in the web UI automatically.

## Writing Scripts

Each script needs the following imports:

```
from modules.agent_script_interpreter import BaseCommand
from modules.agent import BaseAgent
```

Each command in a script is its own class:

```
class SystemRecon(BaseCommand):
    # command name, this is called from the shell
    command_name = "system_recon"
    # Command help, this is what is shown when `help` is called
    command_help = (
        "\tUsage: `system_recon` [exfiltration_url] [temp_filepath]\n"
        "\tAggregates system information and network connections.\n"
    )

    def __init__(self, command, args_list, agent_id):
        # init the parent class
        super().__init__(command, args_list, agent_id)
        # init the BaseAgent for interacting with the agent
        self.agent_class = BaseAgent(agent_id)
        # list for command ID's that have been enqueued
        self.command_ids = []

    # this is how we are gonna do it
    def run(self):
        ... some command
```

Methods for interacting with the agent:
SomethingSomething base agent which provides methods/an api
for interacting with the agents

Below is a **Markdown table** focusing on the methods in the `BaseAgent` class only:

| **Method**                                | **Description**                                                                                                                                                                                         |
|-------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `__init__(self, agent_id, config_file_path=None, **kwargs)` | Initializes a `BaseAgent` with default data fields and registers basic command handlers. Sets up the agent’s `redis_client` and internal Munch-based data structure (`self._data`).                          |
| `data` (property)                         | Returns a Munch-based object containing agent information (e.g., system, network).                                                                                                                      |
| `data` (setter)                           | Updates the agent’s internal Munch-based data object. Converts raw dictionaries to Munch objects as needed.                                                                                              |
| `set_command_script(self, script_name)`   | Associates the agent with a given command script name, then unloads the updated data to Redis.|
| `get_command_script(self)`| Retrieves the script name currently assigned to the agent.|
| `register(self)` | Registers or updates the agent in Redis. Loads the latest data if it exists, sets `agent.new = True` if not found, and saves updated data.|
| `unregister(self)`| Removes the agent from Redis entirely, identified by `self.data.agent.id`. |
| `unload_data(self)`| Serializes the agent’s data (`self.data`) to JSON and stores it in Redis as `AgentData`.|
| `load_data(self)`| Pulls the latest agent data from Redis, updates `self.data`, and returns `True` on success. WARNING: Any unsaved data to the class that has not been unloaded to redis, WILL BE DELETED|
| `enqueue_command(self, command)`| Generates a unique command ID, pushes the ID into the agent’s Redis queue, and stores a record (`AgentCommand`) for the command itself. Returns the new command ID. |
| `dequeue_command(self)` | Pops the next command ID from the agent’s Redis queue, retrieves the corresponding `AgentCommand` from Redis, and returns it. Returns `False` if the queue is empty. |
| `get_all_commands_and_responses(self)`    | Fetches all commands from Redis that match the current agent’s ID, returning a list of dictionaries containing command details (ID, command, response, timestamp).|
| `get_one_command_and_response(self, command_id)` | Retrieves a single command by its ID and checks if it belongs to the current agent. Returns a dictionary with command details (ID, command, response, timestamp) or `None` if not found. |                                                                                    
| `store_response(self, command_id, response)` | Finds the `AgentCommand` by command ID, updates its `response`, optionally invokes a registered handler, and checks if the command should be stored in the agent’s data on callback.|
| `store_command_response_on_callback(self, command, location)` | Appends a tuple `(command, location)` to the agent’s data so that any future responses to `command` automatically get stored at the specified location in the agent’s data. Ex, `shell whoami` to `system.username`|
| `update_notes(self, notes)`| Sets `self.data.agent.notes = notes` and saves the updated data to Redis.|
| `update_new_status(self, new: bool)`| Sets `self.data.agent.new = new` and saves the updated data to Redis.                                                                                                   
| `update_data_field(self, field, value)`   | Updates a nested, dot-notated field in the agent’s data (e.g., `"system.hostname"`) with `value` and saves changes to Redis.|

## Agent Data Model
The Agent Data Model is a flexible, Munch-based structure accessible via agent.data. Its fields are organized into logical categories—like system, network, and hardware—and can be freely extended with new properties to suit your needs. The entire model is dot-accessible, meaning you can access nested keys using attribute notation (e.g., agent.data.system.hostname).

Below is the default structure:
```
self._data = munch.munchify(
    {
        "system": {
            "hostname": None,
            "os": None,
            "architecture": None,
            "username": None,
            "privileges": None,
            "uptime": None,
        },
        "network": {
            "internal_ip": None,
            "external_ip": None,
            "mac_address": None,
            "default_gateway": None,
            "dns_servers": [],
            "domain": None,
            "next_hop": None,
        },
        "hardware": {
            "cpu": None,
            "cpu_cores": None,
            "ram": None,
            "disk_space": None,
        },
        "agent": {
            "id": agent_id,
            "version": None,
            "first_seen": None,
            "last_seen": None,
            "new": None, 
        },
        "security": {
            "av_installed": [],
            "firewall_status": None,
            "sandbox_detected": False,
            "debugger_detected": False,
        },
        "geo": {
            "country": None,
            "city": None,
            "latitude": None,
            "longitude": None,
        },
        "config": {"command_script": None, "store_on_callback": []},
    }
)
```

#### Accessing and Updating Fields
Each of these sub-dictionaries can be accessed or updated using dot notation:

Just make sure to call `self.unload_data()` to save the data into redis when done.

```
agent.data.system.hostname = "MyHost"
agent.data.security.av_installed.append("Windows Defender")
agent.data.network.internal_ip = "192.168.0.10"
```

Or, with the built in `update_data_field` method, which will auto `self.unload_data()` to redis. 

#### Custom Extensions:
Because the data model uses Munch, you can add any custom field without modifying the base code:

Again, make sure to call `self.unload_data()` to save the data into redis when done.


```
agent.data.my_custom_category = {}
agent.data.my_custom_category.new_field = "Hello
```

Or, again with the built in `update_data_field` method, which will auto `self.unload_data()` to redis. 


#### Web GUI Integration
All fields under agent.data automatically appear on the left side of the Agent page in the Web GUI. You can store important or dynamic information (e.g., environment details, credentials, or scanning results) without additional configuration.

[img_of_agent_page](../img/webinterface/)

#### Persistence in Redis
When you register or unload the agent data, the entire Munch object is serialized and stored in Redis. Calling `agent.load_data()` updates the in-memory Munch object with the latest values from Redis.

Alternatively/the prefered method, you can just use the `agent.update_data_field()` method to update/create new fields, which will save to redis for you.

## Examples

### `system_recon`
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