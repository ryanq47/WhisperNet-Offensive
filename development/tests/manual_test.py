import requests
import uuid
import os
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import load_yaml
import time

# Initialize Rich Console
console = Console()

# Load configuration
config = load_yaml.load_yaml()
BASE_URL = f"http://{config.server.ip}:{config.server.port}"

client_id = str(uuid.uuid4())



print(f"CLIENT_ID: {client_id}")
while True:
    print("LOOP")

    rid_early = str(uuid.uuid4())

    dict_data = {
        "rid": rid_early,  # Use the stored rid
        "message": "test_message",
        "timestamp": 1234567890,
        "status": 200,
        "data": {
            "Powershell": [
                {
                    "executable": "ps.exe",
                    "command": "net user /domain add test_user",
                    "id": 1234,
                }
            ]
        },
    }

    # add command
    #print(f"SENDING COMMAND TO BE QUEUED WITHRID: {rid_early}")
    
    #command_url = f"{BASE_URL}/command/{client_id}"
    #command_command =requests.post(url=command_url, json=dict_data)
    #print(command_command.status_code)

    # no more use above vars ==========================

    # get command
    get_url = f"{BASE_URL}/get/{client_id}"
    get_command = requests.get(get_url)
    rid = get_command.json().get("rid")
    print(f"RID FROM REQUEST FROM SERVER: {str(rid)}")

    # do actions

    dict_data_response = {
        "rid": rid,  # Use the stored rid
        "message": "test_message",
        "timestamp": 1234567890,
        "status": 200,
        "data": {
            "Powershell": [
                {
                    "executable": "ps.exe",
                    "command": "net user /domain add test_user",
                    "id": 1234,
                }
            ]
        },
    }

    # post response
    print(f"SENDING BACK MESAGE WITH RID: {str(rid)}")
    post_url = f"{BASE_URL}/post/{client_id}"
    post_command = requests.post(post_url, json = dict_data_response)


    # CHECK WITH ORIG ID GENERATED HERE
    #print(f"TRYING TO GET RESPONSE: {str(rid_early)}")
    #resp_url = f"{BASE_URL}/response/{rid}"
    #resp_command = requests.get(resp_url)
    #print(resp_command.json())

    time.sleep(10)

    # the problem must be the gui then. 
    # this works as intended
    # apparently the gui just works now too wtf