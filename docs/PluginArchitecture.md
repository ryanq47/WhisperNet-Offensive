

# Plugin Documentation

Plugins are an essential feature of WhisperNet, enabling extensibility and customization. The `Instance()` class provides access to necessary components, allowing plugins to integrate seamlessly with the system.

## Plugin Structure

Plugins are straightforward and require a few key components:

1. **A py file**
2. **A modules directory**
3. **A docs directory**

The structure should look like:

```
.
├── docs
│   └── somedocs.md
├── modules
│   └── somemodule.py
└── plugin_file.py
```

Don't worry, there's a script to create a template plugin for you, in `development/scripts/create_plugin.sh`

## The Py File

The py file is the entry point for your plugin, and where the execution logic lives. It *MUST* be named the same as the directory it lives in is. This is a limitation with the plugin loader.

Example: 
 
- Folder name: "MyPlugin"
- Py File name: "MyPlugin.py"

### Basic Template

Here’s a minimal template for the main file in a plugin:

```python
from flask import jsonify
from modules.instances import Instance
from modules.log import log


logger = log(__name__)
app = Instance().app

class Info:
    name = "UserAuthentication"
    author = "ryanq47"

# Optional route example
@app.route('/someroute', methods=['GET'])
def plugin_route():
    return jsonify({"somekey": "somevalue"})
```

### Alternative Response Method

Instead of using `jsonify`, you can utilize the `api_response` function from `modules.utils` to format responses in the standard WhisperNet format:

```json
{
    "data": {},
    "error": {},
    "message": "SomeMessage",
    "rid": "489d3491-c950-4cb8-b485-7dfb1f1aa223",
    "status": 200,
    "timestamp": 1234567890
}
```
## Directories

There's two required(ish)/heavily reccomended directories.

`modules`:
This is the spot for any additional logic/imports the plugin may need. 

`docs`:
This is a spot for any/all documentation for the plugin to go. There's no logic that actually relies on this folder, so it's technically optional, but documentation is always envouraged. 



## Interacting with main program

The plugins can interact with the main program in endless ways. Basically, if you can code it, you can do it. 

However, there are a few "interfaces" that are exposed to make creating plugins easier.

## Singletons:

There's a few singletons which act as gateways for the main program.

#### `Instance`:
---

The Instance singleton holds instances of classes that may be handy to access.

Currently, it has the following attributes:

`app`: The flask application. Literally just a variable that points to the actual flask application. 

- Access with: `Instance().app`


`db_engine`: The SQLAlchemy DB engine. This allows for easier access to db operations. 

- Access with: `Instance().db_engine`


Note, you'll need to import the Instance class, as such:
`from modules.instances import Instance`


#### `Config`:
---

The Config singleton holds the loaded config values, both from the .env file, and the config.yaml file. 


Note, you'll need to import the Instance class, as such:
`from modules.config import Config`

`config.yaml`: The main config file for the program

Access config.yaml values with:
`Config().config.some.value.`

These are mapped to the config file, so the key

```
key:
    key2: value

```
can be accessed with `Config().config.key.key2`

`.env`: The enviornment variables (loaded from .env)


Access with: `Config().env.envvalue`


---