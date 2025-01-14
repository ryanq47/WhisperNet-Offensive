import requests
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

# Load environment variables from .env file (if needed)
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

# Test case for starting a container
def test_docker_start_container():
    console.print(Panel("POST /docker/start/<container_name>", title="Test Case", expand=False))

    container_name = "valid_container_name"
    url = f"{BASE_URL}/docker/start/{container_name}"

    response = send_request_and_print(url, method="post")

    assert response is not None, "No response received"
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert response.json().get("message") == "Container started", "Expected success message for container start"

# Test case for stopping a container
def test_docker_stop_container():
    console.print(Panel("POST /docker/stop/<container_name>", title="Test Case", expand=False))

    container_name = "valid_container_name"
    url = f"{BASE_URL}/docker/stop/{container_name}"

    response = send_request_and_print(url, method="post")

    assert response is not None, "No response received"
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert response.json().get("message") == "Container stopped", "Expected success message for container stop"

# Test case for invalid container name
def test_invalid_container_name():
    console.print(Panel("POST /docker/start/<invalid_container_name>", title="Test Case", expand=False))

    invalid_container_name = "invalid!name"
    url = f"{BASE_URL}/docker/start/{invalid_container_name}"

    response = send_request_and_print(url, method="post")

    assert response is not None, "No response received"
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
    assert response.json().get("message") == "Invalid container name", "Expected invalid name message"

if __name__ == "__main__":
    banner_text = Text("Docker API Test Suite", style="bold magenta", justify="center")
    banner_panel = Panel(banner_text, expand=False, border_style="bright_green", padding=(1, 30))
    console.print(banner_panel)

    results = {}

    test_cases = [
        ("POST /docker/start/<container_name>", test_docker_start_container),
        ("POST /docker/stop/<container_name>", test_docker_stop_container),
        ("POST /docker/start/<invalid_container_name>", test_invalid_container_name),
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
