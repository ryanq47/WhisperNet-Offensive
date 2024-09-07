import os
import random
import string
from ftplib import FTP
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import requests
import load_yaml
import time

# Initialize Rich Console
console = Console()

# Set up base URL from environment or default
config = load_yaml.load_yaml()

# FTP server details
FTP_HOST = "127.0.0.1"  # config.ftp.server.ip
FTP_PORT = 21  # config.ftp.server.port
FTP_USER = "ftp_test_user"  # config.ftp.credentials.username
FTP_PASS = "ftp_test_pass"  # config.ftp.credentials.password

with open('.env', 'r') as f:
    for line in f:
        key, value = line.strip().split('=')
        os.environ[key] = value

# HTTP API Base URL
BASE_URL = f"http://{config.server.ip}:{config.server.port}"

# Set headers globally for HTTP requests
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['jwt_token']}",
}

FTP_DIRECTORY = 'app/ftp/'  # Directory where files are uploaded

def send_request_and_print(url, method="get", json_data=None, headers=None):
    """
    Helper function to send HTTP requests and print the response using rich console.
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
    Test starting the FTP server via HTTP endpoint.
    """
    console.print(Panel("GET /ftp/start", title="Test Case", expand=False))
    url = f"{BASE_URL}/ftp/start"
    response = send_request_and_print(url, headers=headers)
    assert response.status_code == 200 or response.status_code == 400
    assert "message" in response.json()

def test_ftp_stop_server():
    """
    Test stopping the FTP server via HTTP endpoint.
    """
    console.print(Panel("GET /ftp/stop", title="Test Case", expand=False))
    url = f"{BASE_URL}/ftp/stop"
    response = send_request_and_print(url, headers=headers)
    assert response.status_code == 200 or response.status_code == 400
    assert "message" in response.json()

# Test for adding a new FTP user
def test_ftp_add_new_user():
    """
    Test adding a new FTP user via HTTP endpoint.
    """
    console.print(Panel("POST /ftp/new-user", title="Test Case", expand=False))
    url = f"{BASE_URL}/ftp/new-user"
    new_user_data = {
        "username": FTP_USER,
        "password": FTP_PASS
    }
    response = send_request_and_print(url, method="post", json_data=new_user_data, headers=headers)
    assert response.status_code == 200 or response.status_code == 400
    assert "message" in response.json()

# FTP-related tests using `ftplib`
def generate_random_file(filename="testfile.txt", size=1024):
    """
    Generate a file with random content.
    """
    console.print(f"Generating random file: {filename}")
    random_data = ''.join(random.choices(string.ascii_letters + string.digits, k=size))
    with open(filename, 'w') as f:
        f.write(random_data)
    return filename

def test_ftp_login():
    """
    Test login to the FTP server.
    """
    console.print(Panel(f"Logging into FTP server at {FTP_HOST}:{FTP_PORT}", title="Test Case", expand=False))
    try:
        ftp = FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        console.print("[green]FTP login successful[/green]")
        return ftp
    except Exception as e:
        console.print(f"[red]FTP login failed: {e}[/red]")
        return None

def test_ftp_upload_file(ftp, filename="testfile.txt"):
    """
    Test uploading a file to the FTP server.
    """
    console.print(Panel(f"Uploading file to FTP: {filename}", title="Test Case", expand=False))
    try:
        with open(filename, 'rb') as file:
            ftp.storbinary(f'STOR {filename}', file)
        console.print(f"[green]File {filename} uploaded successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Failed to upload file {filename}: {e}[/red]")

def test_file_exists_locally(filename):
    """
    Test if a file exists in the local FTP directory after upload.
    """
    file_path = os.path.join(FTP_DIRECTORY, filename)
    console.print(Panel(f"Checking if file exists in {FTP_DIRECTORY}: {filename}", title="Test Case", expand=False))
    assert os.path.exists(file_path), f"File {filename} does not exist in {FTP_DIRECTORY}"
    console.print(f"[green]File {filename} exists in {FTP_DIRECTORY}.[/green]")

def test_file_deleted_locally(filename):
    """
    Test if a file is deleted from the local FTP directory after deletion.
    """
    file_path = os.path.join(FTP_DIRECTORY, filename)
    console.print(Panel(f"Checking if file is deleted from {FTP_DIRECTORY}: {filename}", title="Test Case", expand=False))
    assert not os.path.exists(file_path), f"File {filename} still exists in {FTP_DIRECTORY} after deletion"
    console.print(f"[green]File {filename} has been deleted from {FTP_DIRECTORY}.[/green]")

def test_ftp_download_file(ftp, filename="testfile.txt"):
    """
    Test downloading a file from the FTP server.
    """
    downloaded_filename = f"downloaded_{filename}"
    console.print(Panel(f"Downloading file from FTP: {filename}", title="Test Case", expand=False))
    try:
        with open(downloaded_filename, 'wb') as file:
            ftp.retrbinary(f'RETR {filename}', file.write)
        console.print(f"[green]File {downloaded_filename} downloaded successfully.[/green]")
        # Clean up the downloaded file
        os.remove(downloaded_filename)
        console.print(f"[green]Downloaded file {downloaded_filename} removed after download.[/green]")
    except Exception as e:
        console.print(f"[red]Failed to download file {filename}: {e}[/red]")

def test_ftp_delete_file(ftp, filename="testfile.txt"):
    """
    Test deleting a file from the FTP server.
    """
    console.print(Panel(f"Deleting file from FTP: {filename}", title="Test Case", expand=False))
    try:
        ftp.delete(filename)
        console.print(f"[green]File {filename} deleted from FTP server.[/green]")
    except Exception as e:
        console.print(f"[red]Failed to delete file {filename}: {e}[/red]")

if __name__ == "__main__":
    banner_text = Text("FTP Server Tests", style="bold magenta", justify="center")
    banner_panel = Panel(
        banner_text, expand=False, border_style="bright_green", padding=(1, 30)
    )
    console.print(banner_panel)

    results = {}
    ftp_client = None

    # HTTP Endpoint to start the FTP server
    try:
        test_ftp_start_server()
        results["GET /ftp/start"] = "✅ Success"
    except AssertionError as e:
        console.print(f"[red]GET /ftp/start Failed: {e}[/red]")
        results["GET /ftp/start"] = "❌ Failed"
    except Exception as e:
        console.print(f"[red]GET /ftp/start Error: {e}[/red]")
        results["GET /ftp/start"] = "❌ Error"

    # Test for adding a new FTP user via HTTP API
    try:
        test_ftp_add_new_user()
        results["POST /ftp/new-user"] = "✅ Success"
    except AssertionError as e:
        console.print(f"[red]POST /ftp/new-user Failed: {e}[/red]")
        results["POST /ftp/new-user"] = "❌ Failed"
    except Exception as e:
        console.print(f"[red]POST /ftp/new-user Error: {e}[/red]")
        results["POST /ftp/new-user"] = "❌ Error"

    # FTP Tests
    ftp_client = test_ftp_login()
    
    if ftp_client:
        try:
            # Generate and upload a random file to the FTP server
            filename = generate_random_file()
            test_ftp_upload_file(ftp_client, filename=filename)
            
            # Verify the file exists in the FTP directory after upload
            test_file_exists_locally(filename)
            
            # Download the file from the FTP server
            test_ftp_download_file(ftp_client, filename=filename)
            
            # Delete the file from the FTP server
            test_ftp_delete_file(ftp_client, filename=filename)
            
            # Verify the file is deleted from the FTP directory
            time.sleep(1)  # Delay to ensure file is deleted properly
            test_file_deleted_locally(filename)
            
            results["FTP Tests"] = "✅ Success"
        except Exception as e:
            console.print(f"[red]FTP Tests Failed: {e}[/red]")
            results["FTP Tests"] = "❌ Failed"
        finally:
            # Close the FTP connection
            if ftp_client:
                ftp_client.quit()
                console.print("[green]FTP connection closed.[/green]")
    else:
        results["FTP Tests"] = "❌ Failed to login to FTP"

    # HTTP Endpoint to stop the FTP server
    try:
        test_ftp_stop_server()
        results["GET /ftp/stop"] = "✅ Success"
    except AssertionError as e:
        console.print(f"[red]GET /ftp/stop Failed: {e}[/red]")
        results["GET /ftp/stop"] = "❌ Failed"
    except Exception as e:
        console.print(f"[red]GET /ftp/stop Error: {e}[/red]")
        results["GET /ftp/stop"] = "❌ Error"

    # Add summary to display results
    table = Table(title="Test Summary")

    table.add_column("Test Case", justify="left", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", style="magenta")

    for test_case, status in results.items():
        table.add_row(test_case, status)

    console.print(table)
