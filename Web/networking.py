import requests
from config import Config
from nicegui import app, ui


def api_call(url, timeout=3, return_dict_from_json=True):
    """
    Makes a synchronous GET request to the specified URL and returns the JSON response.

    Args:
        url (str): The URL to request.
        timeout (int): The timeout for the request in seconds (default: 3).
        If the response is in json, decode back to dict. 99% of the times this is true. Else, return raw data.
    Returns:
        dict: Parsed JSON response from the server.

    Raises:
        ValueError: If the response cannot be parsed as JSON.
        requests.RequestException: For network-related errors or timeouts.
    """
    headers = {
        "Authorization": f"Bearer {app.storage.user.get("jwt_token", "")}",
        "Content-Type": "application/json",
    }

    if not url:
        raise ValueError("A valid URL must be provided.")

    try:
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP errors (4xx/5xx)
        # if the response is in json, decode back to dict. 99% of the times this is true
        if return_dict_from_json:
            return response.json()  # Parse and return the JSON response

        else:
            return response.text
    except requests.JSONDecodeError:
        raise ValueError("The response is not valid JSON.")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        raise  # Re-raise the exception for the caller to handle


def api_post_call(url, data=None, files=None):
    """
    Sends a POST request to the specified endpoint.
      - If 'files' is provided, send as multipart/form-data.
      - Otherwise, send 'data' as JSON.
    Returns the parsed JSON response (if any), or an empty dict on error.
    """
    endpoint = f"{Config.API_HOST}/{url.lstrip('/')}"
    jwt_token = app.storage.user.get("jwt_token", "")
    headers = {
        "Authorization": f"Bearer {jwt_token}",
    }

    try:
        if files:
            # Multipart/form-data request (for file Builds)
            r = requests.post(url=endpoint, data=data, files=files, headers=headers)
        else:
            # JSON-only request
            headers["Content-Type"] = "application/json"
            r = requests.post(url=endpoint, json=data, headers=headers)

        if r.status_code not in (200, 201):
            try:
                error_message = r.json().get("message", r.text)
            except Exception:
                error_message = r.text
            ui.notify(f"Error {r.status_code}: {error_message}", type="negative")
            return {}

        try:
            resp_json = r.json()
            ui.notify("Request succeeded", type="positive")
            return resp_json
        except Exception:
            ui.notify("Request succeeded, but no JSON in response", type="warning")
            return {}
    except Exception as e:
        ui.notify(f"Request exception: {str(e)}", type="negative")
        return {}


def api_delete_call(url):
    """
    Sends a DELETE request to the specified endpoint.
    Returns the parsed JSON response (if any), or an empty dict on error.
    """
    endpoint = f"{Config.API_HOST}/{url.lstrip('/')}"
    jwt_token = app.storage.user.get("jwt_token", "")
    headers = {"Authorization": f"Bearer {jwt_token}"}

    try:
        r = requests.delete(endpoint, headers=headers)
        if r.status_code not in (200, 201):
            try:
                error_message = r.json().get("message", r.text)
            except Exception:
                error_message = r.text
            ui.notify(f"Error {r.status_code}: {error_message}", type="negative")
            return {}
        return r.json() if r.text else {}
    except Exception as e:
        ui.notify(f"Request exception: {str(e)}", type="negative")
        return {}
