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
        self.rid = None  # Initialize rid to None

    def get(self):
        url = f"{BASE_URL}/get/{self.client_id}"
        status_code, response_time, response_json = self._send_request(url, method="get")
        
        # If the request is successful, update the rid
        #if status_code == 200 and response_json:
            #self.rid = response_json.get("rid")  # Store the received rid

        print(f"Sending to {url} with RID: {str(self.rid)}")

        return status_code, response_time

    def post(self):
        if not self.rid:
            console.print("[red]No RID found. Ensure 'get' is called before 'post'.[/red]")
            return None, 0
        
        url = f"{BASE_URL}/post/{self.client_id}"
        dict_data = {
            "rid": str(self.rid),  # Use the stored rid
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
        print(f"Sending to {url} with RID: {str(self.rid)}")
        return self._send_request(url, method="post", json_data=dict_data)

    # gets called first as it's "posting" the command
    def command(self):
        
        url = f"{BASE_URL}/command/{self.client_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['jwt_token']}",
        }

        self.rid = str(uuid.uuid4())
        
        dict_data = {
            "rid": str(self.rid),
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
        print(f"Sending to {url} with RID: {str(self.rid)}")
        return self._send_request(url, method="post", json_data=dict_data, headers=headers)

    def _send_request(self, url, method="get", json_data=None, headers=None):
        try:
            start_time = time.time()
            response = getattr(requests, method)(url, json=json_data, headers=headers)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            response_json = response.json() if response.status_code == 200 else None
            return response.status_code, response_time, response_json
        except Exception as e:
            console.print(f"[red]Request failed: {e}[/red]")
            return None, 0, None

def load_test(num_clients, check_in_interval):
    response_stats = {
        "get": {"success": 0, "failure": 0, "times": []},
        "post": {"success": 0, "failure": 0, "times": []},
        "command": {"success": 0, "failure": 0, "times": []}
    }

    clients = [Client(str(uuid.uuid4())) for _ in range(num_clients)]

    while True:
        for client in clients:
            # Send requests in the specified order: command -> get -> post
            command_status, command_time, _ = client.command()
            update_stats(response_stats, "command", command_status, command_time)

            get_status, get_time = client.get()
            update_stats(response_stats, "get", get_status, get_time)

            post_status, post_time, _ = client.post()
            update_stats(response_stats, "post", post_status, post_time)

        # Calculate average response times
        for key in response_stats:
            if response_stats[key]["times"]:
                response_stats[key]["average_time"] = sum(response_stats[key]["times"]) / len(response_stats[key]["times"])
            else:
                response_stats[key]["average_time"] = 0

        display_stats(response_stats, num_clients)

        # Wait for the specified check-in interval before the next round
        time.sleep(check_in_interval)

def update_stats(response_stats, key, status_code, response_time):
    """Helper function to update stats dictionary."""
    if status_code == 200:
        response_stats[key]["success"] += 1
    else:
        response_stats[key]["failure"] += 1
    response_stats[key]["times"].append(response_time)

def display_stats(response_stats, num_clients):
    console.print(Panel(Text(f"Load Testing with {num_clients} Clients", style="bold magenta"), expand=False))
    
    # Display the response summary table
    table = Table(title=f"Response Summary for {num_clients} Clients")

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

if __name__ == "__main__":
    # Configure the check-in parameters
    num_clients = 1  # Number of clients to simulate
    check_in_interval = 1000  # Interval in seconds between each check-in

    load_test(num_clients, check_in_interval)
