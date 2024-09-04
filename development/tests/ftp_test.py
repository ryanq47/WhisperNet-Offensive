import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import os
import load_yaml

# Initialize Rich Console
console = Console()

# Set up base URL from environment or default
config = load_yaml.load_yaml()

BASE_URL = f"http://{config.server.ip}:{config.server.port}"

def send_request_and_print(url, method="get", json_data=None, headers=None):
    """
    Helper function to send requests and print the response using rich console.
    """
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

def test_ftp_start_server():
    """
    Test starting the FTP server.
    """
    console.print(Panel("GET /ftp/start", title="Test Case", expand=False))
    url = f"{BASE_URL}/ftp/start"
    response = send_request_and_print(url)
    assert response.status_code == 200 #or response.status_code == 400
    assert "message" in response.json()

def test_ftp_stop_server():
    """
    Test stopping the FTP server.
    """
    console.print(Panel("GET /ftp/stop", title="Test Case", expand=False))
    url = f"{BASE_URL}/ftp/stop"
    response = send_request_and_print(url)
    assert response.status_code == 200 #or response.status_code == 400
    assert "message" in response.json()

def test_ftp_new_user():
    """
    Test adding a new user to the FTP server.
    """
    console.print(Panel("POST /ftp/new-user", title="Test Case", expand=False))
    url = f"{BASE_URL}/ftp/new-user"
    headers = {
        "Content-Type": "application/json",
    }
    dict_data = {
        "username": "newuser",
        "password": "newpassword"
    }
    response = send_request_and_print(url, method="post", json_data=dict_data, headers=headers)
    assert response.status_code == 200 #or response.status_code == 400
    assert "message" in response.json() or "error" in response.json()

if __name__ == "__main__":
    banner_text = Text("FTP Server Tests", style="bold magenta", justify="center")
    banner_panel = Panel(
        banner_text, expand=False, border_style="bright_green", padding=(1, 30)
    )
    console.print(banner_panel)

    results = {}

    test_cases = [
        ("GET /ftp/start", test_ftp_start_server),
        ("GET /ftp/stop", test_ftp_stop_server),
        ("GET /ftp/start", test_ftp_start_server), # start server again for new user lol
        ("GET /ftp/new-user", test_ftp_new_user),
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
