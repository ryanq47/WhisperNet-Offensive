

# Plugin Documentation

Plugins are an essential feature of WhisperNet, enabling extensibility and customization. The `Instance()` class provides access to necessary components, allowing plugins to integrate seamlessly with the system.

## Plugin Structure

Plugins are straightforward and require a few key components:

1. **`Info` Class**
2. **Logger and App Variable**
3. **Necessary Imports**

### Basic Template

Here’s a minimal template for a plugin:

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

This format ensures consistency across responses and integrates well with WhisperNet’s API standards.

---