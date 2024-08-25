import requests
import uuid
import os
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import load_yaml

# Initialize Rich Console
console = Console()

# Load configuration
config = load_yaml.load_yaml()
BASE_URL = f"http://{config.server.ip}:{config.server.port}"

# Load environment variables
with open('.env', 'r') as f:
    for line in f:
        key, value = line.strip().split('=')
        os.environ[key] = value

class Client:
    def __init__(self, client_id):
        self.client_id = client_id

    def get(self):
        url = f"{BASE_URL}/get/{self.client_id}"
        return self._send_request(url, method="get")

    def post(self):
        url = f"{BASE_URL}/post/{self.client_id}"
        dict_data = {
            "rid": str(uuid.uuid4()),
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
        return self._send_request(url, method="post", json_data=dict_data)

    def command(self):
        url = f"{BASE_URL}/command/{self.client_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['jwt_token']}",
        }
        dict_data = {
            "rid": str(uuid.uuid4()),
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
        return self._send_request(url, method="post", json_data=dict_data, headers=headers)

    def _send_request(self, url, method="get", json_data=None, headers=None):
        try:
            start_time = time.time()
            response = getattr(requests, method)(url, json=json_data, headers=headers)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            return response.status_code, response_time
        except Exception as e:
            console.print(f"[red]Request failed: {e}[/red]")
            return None, 0

def load_test(num_clients):
    response_stats = {
        "get": {"success": 0, "failure": 0, "times": []},
        "post": {"success": 0, "failure": 0, "times": []},
        "command": {"success": 0, "failure": 0, "times": []}
    }

    for i in range(num_clients):
        client = Client(str(uuid.uuid4()))
        # Send requests in the specified order: command -> get -> post
        command_status, command_time = client.command()
        update_stats(response_stats, "command", command_status, command_time)

        get_status, get_time = client.get()
        update_stats(response_stats, "get", get_status, get_time)

        post_status, post_time = client.post()
        update_stats(response_stats, "post", post_status, post_time)

    # Calculate average response times
    for key in response_stats:
        if response_stats[key]["times"]:
            response_stats[key]["average_time"] = sum(response_stats[key]["times"]) / len(response_stats[key]["times"])
        else:
            response_stats[key]["average_time"] = 0

    return response_stats

def update_stats(response_stats, key, status_code, response_time):
    """Helper function to update stats dictionary."""
    if status_code == 200:
        response_stats[key]["success"] += 1
    else:
        response_stats[key]["failure"] += 1
    response_stats[key]["times"].append(response_time)

def incremental_load_test(start_clients, max_clients, increment, delay_between_steps):
    current_clients = start_clients

    while current_clients <= max_clients:
        console.print(Panel(Text(f"Load Testing with {current_clients} Clients", style="bold magenta"), expand=False))

        response_stats = load_test(current_clients)

        # Display the response summary table
        table = Table(title=f"Response Summary for {current_clients} Clients")

        table.add_column("Endpoint", justify="left", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center", style="magenta")
        table.add_column("Count", justify="center", style="green")
        table.add_column("Avg. Response Time (ms)", justify="center", style="yellow")

        for endpoint, stats in response_stats.items():
            success_count = stats["success"]
            failure_count = stats["failure"]
            avg_response_time = stats["average_time"]
            table.add_row(endpoint, "Success", f"{success_count}/{current_clients}", f"{avg_response_time:.2f}")
            table.add_row(endpoint, "Failure", f"{failure_count}/{current_clients}", "")

        console.print(table)

        # Increment the number of clients for the next test
        current_clients += increment

        # Wait for a bit before the next round
        time.sleep(delay_between_steps)

if __name__ == "__main__":
    # Configure the incremental load test parameters
    start_clients = 100  # Starting with one client
    max_clients = 100  # Maximum number of clients to test incrementally
    increment = 1  # Increment by one client at each step
    delay_between_steps = 2  # Delay in seconds between each step

    incremental_load_test(start_clients, max_clients, increment, delay_between_steps)
