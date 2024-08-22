import requests
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import load_yaml


## Tests to still do/implement:
# - [ ] Wrong value inputs
# - [ ] Redis input/value checking - gonna take some work
#


# Initialize Rich Console
console = Console()

config = load_yaml.load_yaml()

BASE_URL = f"http://{config.server.ip}:{config.server.port}"


def test_simple_http_get():
    console.print(Panel("GET /get/<client_id>", title="Test Case", expand=False))

    client_id = "test-client-id"
    url = f"{BASE_URL}/get/{client_id}"

    response = requests.get(url)

    console.print_json(data=response.json())

    assert response.status_code == 200
    assert response.json() == {"client_id": client_id}


def test_simple_http_post():
    console.print(Panel("POST /post/<client_id>", title="Test Case", expand=False))

    client_id = "test-client-id"
    url = f"{BASE_URL}/post/{client_id}"

    dict_data = {
        "rid": "12345-56789-09187",
        "message": "somemessage",
        "timestamp": 1234567890,
        "status": 200,
        "data": {
            # Example Sync Keys types
            # Powershell Key which will contain info for running powershell
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
            # Some other Sync Key, that does Some Other thing
            "SomeSync": [{"somedata": "somedata"}, {"somedata": "somedata"}],
        },
    }

    # bugged out here
    response = requests.post(url, json=dict_data)  # Use 'json=' to send JSON data

    # Instead of serializing the whole response, we parse the JSON content
    try:
        json_response = response.json()
        console.print_json(data=json_response)
    except ValueError:
        console.print(f"Response content is not valid JSON: {response.text}")

    assert response.status_code == 200
    # assert json_response == {"client_id": client_id} # figure this exact struct test out later, just use response code right now.


def test_simple_http_queue_command():
    console.print(Panel("POST /command/<client_id>", title="Test Case", expand=False))

    client_id = "test-client-id"
    url = f"{BASE_URL}/command/{client_id}"

    dict_data = {
        "rid": "12345-56789-09187",
        "message": "somemessage",
        "timestamp": 1234567890,
        "status": 200,
        "data": {
            # Example Sync Keys types
            # Powershell Key which will contain info for running powershell
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
            # Some other Sync Key, that does Some Other thing
            "SomeSync": [{"somedata": "somedata"}, {"somedata": "somedata"}],
        },
    }

    # bugged out here
    response = requests.post(url, json=dict_data)  # Use 'json=' to send JSON data

    # Instead of serializing the whole response, we parse the JSON content
    try:
        json_response = response.json()
        console.print_json(data=json_response)
    except ValueError:
        console.print(f"Response content is not valid JSON: {response.text}")

    assert response.status_code == 200
    # assert json_response == {"client_id": client_id} # figure this exact struct test out later, just use response code right now.


if __name__ == "__main__":
    banner_text = Text("simple_http", style="bold magenta", justify="center")
    # Create a panel for the banner
    banner_panel = Panel(
        banner_text, expand=False, border_style="bright_green", padding=(1, 30)
    )
    # Print the banner to the console
    console.print(banner_panel)

    results = {}

    try:
        test_simple_http_get()
        results["GET /get/<client_id>"] = "✅ Success"
    except Exception as e:
        console.print(f"[red]GET /get/<client_id> Failed: {e}[/red]")
        results["GET /get/<client_id>"] = "❌ Failed"

    try:
        test_simple_http_post()
        results["POST /post/<client_id>"] = "✅ Success"
    except Exception as e:
        console.print(f"[red]POST /post/<client_id> Failed: {e}[/red]")
        results["POST /post/<client_id>"] = "❌ Failed"

    try:
        test_simple_http_queue_command()
        results["POST /command/<client_id>"] = "✅ Success"
    except Exception as e:
        console.print(f"[red]POST /command/<client_id> Failed: {e}[/red]")
        results["POST /command/<client_id>"] = "❌ Failed"

    # Adding a summary table for all test cases
    table = Table(title="Test Summary")

    table.add_column("Test Case", justify="left", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", style="magenta")

    for test_case, status in results.items():
        table.add_row(test_case, status)

    console.print(table)
