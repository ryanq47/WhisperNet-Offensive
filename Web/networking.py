import requests
from config import Config
from nicegui import app


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
        response = requests.get(url, timeout=timeout)
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
