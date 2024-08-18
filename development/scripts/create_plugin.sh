#!/bin/bash

# Create folder for plugin
echo "Enter plugin name:"
read plugin_name

echo "Enter plugin author:"
read plugin_author

mkdir -p $plugin_name/modules
mkdir -p $plugin_name/docs

touch $plugin_name/$plugin_name.py

echo "Created structure, adding minimum content..."

# Echo the content into $plugin_name/$plugin_name.py
cat <<EOF > $plugin_name/$plugin_name.py
from flask import jsonify
from modules.instances import Instance
from modules.log import log

logger = log(__name__)
app = Instance().app

class Info:
    name = "$plugin_name"
    author = "$plugin_author"

# Optional route example
@app.route('/someroute', methods=['GET'])
def plugin_route():
    return jsonify({"somekey": "somevalue"})
EOF

echo "Plugin $plugin_name created successfully!"
echo "Go ahead any copy to app/plugins/ folder for it to be included on startup."
