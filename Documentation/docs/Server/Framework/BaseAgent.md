# BaseAgent Class Documentation

The `BaseAgent` class provides a foundation for client interaction in a Redis-backed system, supporting configuration loading, command queuing, data management, and interaction via templates and aliases.

Any plugin that has C2 capability, should use this for handling a lot of the backend BS.

---

## [X] Class Overview

The `BaseAgent` class:

- Connects to a Redis backend to store and retrieve data.
- Loads configuration files to support aliasing and templating of commands.
- Provides a **data** attribute (via `self.data`) for structured client state management.
- Manages command queues for sending and processing tasks.

---

## [X] Using in a class:

This class is meant to be inhereted. 

Requirements: 

- `agent_id`: A _unique_ ID, used to track the agent accross the platform. For example, a UUID4. 

You can use it in your own class as such:

```
class Agent(BaseAgent):
    def __init__(self, agent_id):
        super().__init__(agent_id=agent_id)
```

---

## [X]Attributes

- **self.redis_client**: Redis client for database interactions.
    - NOTE! `decode_responses` is enabled, so all respones will come back as strings. 
- **self.alias**: Stores aliases loaded from a config file.
- **self.template**: Stores templates for commands loaded from a config file.
- **self._data**: A `dict` object holding structured client data. See the "Data Model Breakdown" as to how to use this

---

## [X] Data Model Breakdown:

Here are the current default data items in the datamodel.

As this is a munch object, you can access `self.data` items using dot notation: `self.data.system.hostname`.

Additionally, if you want to access as a raw dictonary, use `self._data`. 

#### self.data vs self._data:

| Attribute    | Type             | Example Access      |
| ------------ | ---------------- | ------------------- |
| `self._data` | **Python dict**  | `self._data["key"]` |
| `self.data`  | **Munch object** | `self.data.key`     |

#### Data Model Structure:

Below is the base structure of the data. The only field that is not `None` at initilization, is `agent.id`. This value is supplied from the `agent_id` arguement in `init`.

```
{
    "system": {
        "hostname": None,
        "os": None,
        "os_version": None,
        "architecture": None,
        "username": None,
        "privileges": None,
        "uptime": None
    },
    "network": {
        "internal_ip": None,
        "external_ip": None,
        "mac_address": None,
        "default_gateway": None,
        "dns_servers": [],
        "domain": None
    },
    "hardware": {
        "cpu": None,
        "cpu_cores": None,
        "ram": None,
        "disk_space": None
    },
    "agent": {
        "id": agent_id,
        "version": None,
        "first_seen": None,
        "last_seen": None
    },
    "security": {
        "av_installed": [],
        "firewall_status": None,
        "sandbox_detected": False,
        "debugger_detected": False
    },
    "geo": {
        "country": None,
        "city": None,
        "latitude": None,
        "longitude": None
    },
    "config": {
        "file": None
    }
}
```

These values can *only* be accessed/set with either `self.data`, or `self._data`, they *cannot* be set at the class initilazation.

Example Usage:

```
MyClass(BaseAgent):
    def __init__(self, agent_id):
        super().init(agent_id)
        self.data.agent.first_seen = "Now" # or a timestamp
        self.data.geo.city = "New York"
```

---

## Methods

### Initialization

#### [X] `__init__(self, agent_id, **kwargs)`

Initializes a `BaseAgent` instance:

- Connects to Redis.
- Sets dynamic attributes via `kwargs`.
- Prepares the `self._data` structure.
- (Not implemented) Searches redis to see if an entry already exists, if so, loads that entry into the current class/datamodel.

---

### Redis Data Management

#### `_load_data_from_redis(self, agent_id)`

Loads client data from Redis into `self.data`.

#### [X] `register(self)`

Registers an agent in the system and stores it in Redis using the `Agent` model from `modules.redis_models`. The agent is uniquely identified by `self.data.agent.id`.

#### [X] `unregister(self)`

Removes the agent from the system by calling the `Agent` model from `modules.redis_models`, using `self.data.agent.id` for identification.

#### `load_data(self)`  - Not Implemented

Loads client data from Redis into the class instance.

#### `unload_data(self)` - Not Implemented

Saves class data back to Redis.

---

### [X] Configuration Management

Config files (or "templates") let you quickly change an agent’s functionality. Similar to Cobalt Strike’s malleable profiles—but simpler—they are YAML-based and rely on macros to replace values.

Example Template:

```
info:
  template_name: "Testing Template"
  template_author: "ryanq.47"

# alias go here. These are effectively macros for running commands from the console
alias:
  local_user_enum: powershell "whoami /all; net users; net groups"
  

# command templates, these are how each command is modified before being run/sent to the client
template:
  # insert powershell command into %%COMMAND%%
  powershell: powershell iex bypass; powershell %%COMMAND%%

## Just some notes on how these work - you can delete these
### Alias to Client Workflow (Step-by-Step)

# 1. User Input
#    - The user types a command, e.g., `local_user_enum`.

# 2. Command Translation
#    - The input command is translated to its corresponding *console* command:
#      ```
#      powershell "whoami /all; net users; net groups"
#      ```

# 3. Command Parsing (Behind the Scenes)
#    - The command undergoes parsing:
#      - The leading `powershell` is stripped.
#      - Only the arguments are saved for processing.
#      - Example:
#        - Input: `powershell "whoami /all; net users; net groups"`
#        - Saved: `"whoami /all; net users; net groups"`

# 4. Wrapping the Command in a Template
#    - The parsed command is wrapped using a predefined PowerShell template:
#      ```
#      powershell iex bypass; powershell %%COMMAND%%
#      ```
#    - The placeholder `%%COMMAND%%` is replaced with the parsed arguments:
#      ```
#      powershell iex bypass; powershell "whoami /all; net users; net groups"
#      ```

# 5. Sending to the Client
#    - The fully processed command is sent to the client for execution.


# This isn't quite as good as Cobalt Strikes CNA & Malleable profiles, but does allow for some customization.

```

#### [X] `load_config(self, config_file_path)`

`config_file_path`: Either a string path, or a `pathlib.Path` object

Loads a YAML configuration file:

- Expects `template` and `alias` sections.
    - If either of these sections are not found, an error will be printed to the console.
- Calls `_load_alias` and `_load_template` to populate attributes.

Example usage:

```
class Agent(BaseAgent):
    def __init__(self, agent_id):
        super().__init__(agent_id=agent_id)
				self.load_config("./myconfig.yaml")
```

#### [X] `_load_alias(self, alias_dict)`

Loads aliases from a dictionary into `self.alias`. Internal function, do not use

#### [X] `_load_template(self, template_dict)`

Loads templates from a dictionary into `self.template`. Internal function, do not use

#### [X] `validate_config(config_file_path)`

Static method to validate the structure of a YAML configuration file.

- On success: (Bool): Returns `True`
- On Failure: (Bool): Returns `False`

This checks that the following items are in the template:

- `template` section
- `alias` section
- `info` section

---

### [X] Command Handling

#### [X] `format_command(self, command, arguments)`

Formats a command based on its template. This is meant to be called when a command comes in, and needs to be formatted to the current template.

- Replaces `%%COMMAND%%` in the template with provided arguments.
- Returns the formatted command.

Example Scenario:

- User types in the following command: `powershell:whoami`
- Template is configured to turn powershell commands into: `powershell iex bypass; powershell %%COMMAND%%`
- Function replaces `%%COMMAND%%` with `whoami`
- Function returns: `powershell iex bypass; powershell whoami`
- This command is then queued into redis

Psuedo Code:

```
command = "execute:powershell:whoami"
formatted_command = self.format_command(command)
print("Command has been transformed from {command} to {formatted_command}")
self.enqueue_command(formatted_command) # Finally, enqueue to redis
```

Implementation / Strategy notes:

There are two main ways to handle command transformations:

1. On inbound command: This will transform the command when it's inbound from a user. As such, it will get stored in Redis as the transformed command. 
2. After Dequeue: Antoher option is to store the inbound command into redis, and on dequeue, take the currently loaded profile and transform the command

Both have pros/cons, either are valid options. 

... Pros Cons table here ...

---

### [X] Redis Command Queue Management

#### [X] `Queue info`

Redis Queue's are used to hold commands to be run. This is acheived with redis's `rpush`, and `blpop` functions. 

Each queue item is put into the redis DB as such: `whispernet:client:id_of_client`. 

#### [X] `enqueue_command(self, command)`

Enqueues a command into the Redis stream for this client.

Example Usage:

```
command = "run:powershell"
self.enqueue_command(command)
```

#### [X] `dequeue_command(self)`

Dequeues and processes commands from the Redis stream.

Returns one of two items:

- On success: (str) The command that was dequeued 
- On Failure: (Bool): `False`
    - A failure is returned if there is no command in the queue. It isup to the plugin to handle the response to the agent at this point. A good default is to send a `sleep` command.

Example Usage:

```
command = self.dequeue_command()
print(f"The dequeued command is: {command}")

```

---

### Data Conversion - Not Implemented

#### `to_dict(self)`

Converts the class instance's attributes into a dictionary.

#### `to_json(self)`

Converts the class instance into a JSON string.

#### `from_dict(cls, data)`

Class method to create an instance from a dictionary.

#### `from_json(cls, json_data)`

Class method to create an instance from a JSON string.

---

---