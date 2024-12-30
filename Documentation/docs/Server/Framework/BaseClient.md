# BaseClient Class Documentation

The `BaseClient` class provides a foundation for client interaction in a Redis-backed system, supporting configuration loading, command queuing, data management, and interaction via templates and aliases.

Any plugin that has C2 capability, should use this for handling a lot of the backend BS.



---

## Class Overview
The `BaseClient` class:

- Connects to a Redis backend to store and retrieve data.

- Loads configuration files to support aliasing and templating of commands.

- Provides a **data** attribute (via `self.data`) for structured client state management.

- Manages command queues for sending and processing tasks.

---
## Using in a class:

You can use it in a class as such:

```
class Agent(BaseClient):
    def __init__(self, id):
        super().__init__(id)
```

---

## Attributes
- **self.redis_client**: Redis client for database interactions.
- **self.alias**: Stores aliases loaded from a config file.
- **self.template**: Stores templates for commands loaded from a config file.
- **self._data**: A `munch` object holding structured client data.



---
## Data Model Breakdown:

Here are the current default data items in the datamodel.


As this is a munch object, you can access `self.data` items using dot notation: `self.data.system.hostname`.

(NOT IMPL) All of these item are stored in the redis DB, which allows for dynamic loading of classes based on that data.

```
{
    "system": {
        "hostname": None,
        "os": None,
        "os_version": None,
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
    "config": {
        "file": None,  # config file
    },
}

```


---
## Methods

### Initialization
#### `__init__(self, agent_id, **kwargs)`
Initializes a `BaseClient` instance:
- Connects to Redis.
- Sets dynamic attributes via `kwargs`.
- Prepares the `self._data` structure.
- Optionally loads agent data from Redis if `agent_id` is provided.

---

### Redis Data Management
#### `_load_data_from_redis(self, agent_id)`
Loads client data from Redis into `self.data`.

#### `register(self)`
Registers a client in the system and stores it in Redis.

#### `unregister(self)`
Unregisters the client from the system.

#### `load_data(self)`
Loads client data from Redis into the class instance.

#### `unload_data(self)`
Saves class data back to Redis.

---

### Configuration Management
#### `load_config(self, config_file_path)`
Loads a YAML configuration file:
- Expects `template` and `alias` sections.
- Calls `_load_alias` and `_load_template` to populate attributes.

#### `_load_alias(self, alias_dict)`
Loads aliases from a dictionary into `self.alias`.

#### `_load_template(self, template_dict)`
Loads templates from a dictionary into `self.template`.

#### `validate_config(config_file_path)`
Static method to validate the structure of a YAML configuration file.

---

### Command Handling
#### `format_command(self, command, arguments)`
Formats a command based on its template:
- Replaces `%%COMMAND%%` in the template with provided arguments.
- Returns the formatted command.

---

### Redis Command Queue Management
#### `enqueue(self, command)`
Enqueues a command into the Redis stream for this client.

#### `dequeue(self)`
Dequeues and processes commands from the Redis stream.

---

### Data Conversion
#### `to_dict(self)`
Converts the class instance's attributes into a dictionary.

#### `to_json(self)`
Converts the class instance into a JSON string.

#### `from_dict(cls, data)`
Class method to create an instance from a dictionary.

#### `from_json(cls, json_data)`
Class method to create an instance from a JSON string.

---

### Properties
#### `data`
Provides access to the `self._data` attribute, a structured `munch` object for client state.

**Example:**
```python
hostname = client.data.system.hostname
client.data.network.internal_ip = "192.168.1.10"
```

---

## Notes
- The `self.data` property simplifies access to client state data using dot notation.
- Redis key structure for commands follows the pattern: `client:command_stream:<client_id>`.
- The configuration file **must** contain `template` and `alias` sections.
