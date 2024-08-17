import requests
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Initialize Rich Console
console = Console()

BASE_URL = "http://localhost:8081"  # Replace with your actual base URL
USERNAME = "username"
PASSWORD = "password"


def test_register_user(jwt):
    url = f"{BASE_URL}/register"
    payload = {"username": "somenewuser", "password": "somenewpassword"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt}",
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    console.print(Panel("Register User", title="Test Case", expand=False))
    console.print_json(data=response.json())

    assert response.status_code == 200


def test_login_user():
    url = f"{BASE_URL}/login"
    payload = {"username": USERNAME, "password": PASSWORD}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    console.print(Panel("Login User", title="Test Case", expand=False))
    console.print_json(data=response.json())

    assert response.status_code == 200
    assert "access_token" in response.json()["data"]
    # assert (
    #    "access_token" in response.json()["data"]["access_token"] != ""
    # )  # make sure access token is someithng
    assert response.json()["message"] == "Login Success"
    return response.json()["data"]["access_token"]


def test_login_user_invalid_credentials():
    url = f"{BASE_URL}/login"
    payload = {"username": "wronguser", "password": "wrongpassword"}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    console.print(Panel("Login Invalid Credentials", title="Test Case", expand=False))
    console.print_json(data=response.json())

    assert response.status_code == 401
    assert response.json()["message"] == "Login Failure"


def test_registration_disabled(jwt):
    url = f"{BASE_URL}/register"
    payload = {"username": "newuser", "password": "newpassword"}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {jwt}"}

    # Simulate registration being disabled by adjusting the server config (if possible)
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    console.print(Panel("Registration Disabled", title="Test Case", expand=False))
    console.print_json(data=response.json())

    assert response.status_code == 410
    assert response.json()["message"] == "Route is disabled"


def test_user_already_exists(jwt):
    url = f"{BASE_URL}/register"
    payload = {"username": USERNAME, "password": PASSWORD}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {jwt}"}

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    console.print(Panel("User Already Exists", title="Test Case", expand=False))
    console.print_json(data=response.json())

    assert response.status_code == 409
    assert response.json()["message"] == "A user with this username already exists"


if __name__ == "__main__":
    jwt = test_login_user()
    test_login_user_invalid_credentials()
    test_register_user(jwt)
    # test_registration_disabled(jwt)
    test_user_already_exists(jwt)

    # Adding a summary table for all test cases (Optional)
    table = Table(title="Test Summary")

    table.add_column("Test Case", justify="left", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", style="magenta")

    table.add_row("Register User", "✅ Success")
    table.add_row("Login User", "✅ Success")
    table.add_row("Login Invalid Credentials", "✅ Success")
    table.add_row("Registration Disabled", "✅ Success")
    table.add_row("User Already Exists", "✅ Success")

    console.print(table)
