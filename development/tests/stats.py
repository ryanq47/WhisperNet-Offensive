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

def test_get_clients():
    console.print(Panel("GET /clients", title="Test Case", expand=False))

    url = f"{BASE_URL}/clients"

    response = send_request_and_print(url)

    assert response is not None, "No response received"
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert isinstance(response.json().get('data'), dict), "Expected a dictionary in the response data"
    assert all(isinstance(client, dict) for client in response.json().get('data', {}).values()), "All client data should be dictionaries"

if __name__ == "__main__":
    banner_text = Text("Client Data Fetch Test", style="bold magenta", justify="center")
    banner_panel = Panel(banner_text, expand=False, border_style="bright_green", padding=(1, 30))
    console.print(banner_panel)

    results = {}

    test_cases = [
        ("GET /clients", test_get_clients),
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
