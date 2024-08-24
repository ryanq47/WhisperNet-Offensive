import requests
import uuid
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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

    def client_worker(client):
        # Send requests to all endpoints
        get_status, get_time = client.get()
        post_status, post_time = client.post()
        command_status, command_time = client.command()
        return {
            "get": (get_status, get_time),
            "post": (post_status, post_time),
            "command": (command_status, command_time)
        }

    clients = [Client(str(uuid.uuid4())) for _ in range(num_clients)]
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(client_worker, client): client for client in clients}
        for future in as_completed(futures):
            client = futures[future]
            try:
                result = future.result()
                # Update success/failure counts and record response times
                for key, (status_code, response_time) in result.items():
                    if status_code == 200:
                        response_stats[key]["success"] += 1
                    else:
                        response_stats[key]["failure"] += 1
                    response_stats[key]["times"].append(response_time)
            except Exception as exc:
                console.print(f"[red]Client {client.client_id} generated an exception: {exc}[/red]")

    # Calculate average response times
    for key in response_stats:
        if response_stats[key]["times"]:
            response_stats[key]["average_time"] = sum(response_stats[key]["times"]) / len(response_stats[key]["times"])
        else:
            response_stats[key]["average_time"] = 0

    return response_stats

if __name__ == "__main__":
    num_clients = 100  # Adjust the number of clients for load testing
    console.print(Panel(Text("Load Testing with Multiple Clients", style="bold magenta"), expand=False))

    response_stats = load_test(num_clients)

    # Display the response summary table
    table = Table(title="Response Summary")

    table.add_column("Endpoint", justify="left", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", style="magenta")
    table.add_column("Count", justify="center", style="green")
    table.add_column("Avg. Response Time (ms)", justify="center", style="yellow")

    for endpoint, stats in response_stats.items():
        success_count = stats["success"]
        failure_count = stats["failure"]
        avg_response_time = stats["average_time"]
        table.add_row(endpoint, "Success", f"{success_count}/{num_clients}", f"{avg_response_time:.2f}")
        table.add_row(endpoint, "Failure", f"{failure_count}/{num_clients}", "")

    console.print(table)
