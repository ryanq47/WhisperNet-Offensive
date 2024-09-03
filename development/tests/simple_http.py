import requests
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import load_yaml
import os

# Initialize Rich Console
console = Console()

config = load_yaml.load_yaml()

BASE_URL = f"http://{config.server.ip}:{config.server.port}"

# Load environment variables
with open('.env', 'r') as f:
    for line in f:
        key, value = line.strip().split('=')
        os.environ[key] = value

# Helper function for sending requests and printing response
def send_request_and_print(url, method="get", json_data=None, headers=None):
    try:
        response = getattr(requests, method)(url, json=json_data, headers=headers)
        try:
            json_response = response.json()
            console.print_json(data=json_response)
        except ValueError:
            console.print(f"Response content is not valid JSON: {response.text}")
        return response
    except Exception as e:
        console.print(f"[red]Request failed: {e}[/red]")
        return None

def test_simple_http_get():
    console.print(Panel("GET /get/<client_id>", title="Test Case", expand=False))

    client_id = "test-client-id"
    url = f"{BASE_URL}/get/{client_id}"

    response = send_request_and_print(url)

    assert response.status_code == 200
    #assert response.json() == {"client_id": client_id}
    assert response.json()["data"]["Powershell"]

# post data back to client
def test_simple_http_post():
    console.print(Panel("POST /post/<client_id>", title="Test Case", expand=False))

    #client_id = "test-client-id"
    #url = f"{BASE_URL}/post/{client_id}"
    url = f"{BASE_URL}/post/12345-56789-09187"

    dict_data = {
        "rid": "12345-56789-09187",
        "message": "RESPONSE",
        "timestamp": 1234567890,
        "status": 200,
        "data": {
            "blob": [
                {
                    "data": "aaaaaaaahhhhh",
                    "size":"1234",
                    "encoding":"text"

                },
                {
                    "data": "ahhhhhhhhhhhhh",
                    "size":"1234",
                    "encoding":"text"

                },
            ],
        },
    }

    response = send_request_and_print(url, method="post", json_data=dict_data)

    assert response.status_code == 200

def test_simple_http_queue_command():
    console.print(Panel("POST /command/<client_id>", title="Test Case", expand=False))

    client_id = "test-client-id"
    url = f"{BASE_URL}/command/{client_id}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['jwt_token']}",
    }

    dict_data = {
        "rid": "12345-56789-09187",
        "message": "somemessage",
        "timestamp": 1234567890,
        "status": 200,
        "data": {
            "Powershell": [
                {
                    "executable": "ps.exe",
                    "command": "net user /domain add bob",
                    "id": 1234,
                },
                {
                    "executable": "ps.exe",
                    "command": "net group /add Domain Admins Bob",
                    "id": 1235,
                },
            ],
            "SomeSync": [{"somedata": "somedata"}, {"somedata": "somedata"}],
        },
    }

    response = send_request_and_print(url, method="post", json_data=dict_data, headers=headers)

    assert response.status_code == 200

# Additional test cases for incorrect inputs
def test_invalid_jwt_token():
    console.print(Panel("POST /command/<client_id> with Invalid JWT", title="Test Case", expand=False))

    client_id = "test-client-id"
    url = f"{BASE_URL}/command/{client_id}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer invalid_token",
    }

    dict_data = {
        "rid": "12345-56789-09187",
        "message": "somemessage",
        "timestamp": 1234567890,
        "status": 200,
        "data": {"SomeSync": [{"somedata": "somedata"}]},
    }

    response = send_request_and_print(url, method="post", json_data=dict_data, headers=headers)

    assert response.status_code == 422  # Invalid data

def test_missing_required_fields():
    console.print(Panel("POST /post/<client_id> with Missing Fields", title="Test Case", expand=False))

    client_id = "test-client-id"
    url = f"{BASE_URL}/post/{client_id}"

    dict_data = {
        "rid": "12345-56789-09187",  # Missing 'message', 'timestamp', 'status', 'data'
    }

    response = send_request_and_print(url, method="post", json_data=dict_data)

    assert response.status_code == 400

def test_invalid_data_types():
    console.print(Panel("POST /post/<client_id> with Invalid Data Types", title="Test Case", expand=False))

    client_id = "test-client-id"
    url = f"{BASE_URL}/post/{client_id}"

    dict_data = {
        "rid": 12345,  # Invalid type (should be a string)
        "message": "somemessage",
        "timestamp": "invalid_timestamp",  # Invalid type (should be int)
        "status": "200",  # Invalid type (should be int)
        "data": "invalid_data",  # Invalid type (should be dict)
    }

    response = send_request_and_print(url, method="post", json_data=dict_data)

    assert response.status_code == 400

def test_large_payload():
    console.print(Panel("POST /post/<client_id> with Large Payload", title="Test Case", expand=False))

    client_id = "test-client-id"
    url = f"{BASE_URL}/post/{client_id}"

    large_data = {
        "rid": "12345-56789-09187",
        "message": "somemessage" * 1000,
        "timestamp": 1234567890,
        "status": 200,
        "data": {"SomeSync": [{"somedata": "somedata"} for _ in range(1000)]},
    }

    response = send_request_and_print(url, method="post", json_data=large_data)

    assert response.status_code == 200

def test_simple_http_get_response():
    console.print(Panel("GET /response/<response_id>", title="Test Case", expand=False))

    response_id = "12345-56789-09187"
    url = f"{BASE_URL}/response/{response_id}"

    headers = {
        "Authorization": f"Bearer {os.environ['jwt_token']}",
    }

    response = send_request_and_print(url, method="get", headers=headers)

    assert response.status_code == 200
    assert response.json()["rid"]
    assert response.json()["data"]


if __name__ == "__main__":
    banner_text = Text("simple_http", style="bold magenta", justify="center")
    banner_panel = Panel(
        banner_text, expand=False, border_style="bright_green", padding=(1, 30)
    )
    console.print(banner_panel)

    results = {}

    test_cases = [
        ("POST /post/<client_id>", test_simple_http_post),
        ("POST /command/<client_id>", test_simple_http_queue_command),
        ("GET /get/<client_id>", test_simple_http_get),  # run AFTER command is queued
        ("GET /response/<response_id>", test_simple_http_get_response),  # New test case
        #("POST /command/<client_id> with Invalid JWT", test_invalid_jwt_token),
        #("POST /post/<client_id> with Missing Fields", test_missing_required_fields),
        #("POST /post/<client_id> with Invalid Data Types", test_invalid_data_types),
        #("POST /post/<client_id> with Large Payload", test_large_payload),
    ]

    for title, test_case in test_cases:
        try:
            test_case()
            results[title] = "✅ Success"
        except AssertionError as e:
            console.print(f"[red]{title} Failed: {e}[/red]")
            results[title] = "❌ Failed"
        except Exception as e:
            console.print(f"[red]{title} Error: {e}[/red]")
            results[title] = "❌ Error"

    table = Table(title="Test Summary")

    table.add_column("Test Case", justify="left", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", style="magenta")

    for test_case, status in results.items():
        table.add_row(test_case, status)

    console.print(table)
