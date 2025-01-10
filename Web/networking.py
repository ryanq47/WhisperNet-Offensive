import requests


def api_call(url, timeout=3):
    """
    Makes a synchronous GET request to the specified URL and returns the JSON response.

    Args:
        url (str): The URL to request.
        timeout (int): The timeout for the request in seconds (default: 3).

    Returns:
        dict: Parsed JSON response from the server.

    Raises:
        ValueError: If the response cannot be parsed as JSON.
        requests.RequestException: For network-related errors or timeouts.
    """
    if not url:
        raise ValueError("A valid URL must be provided.")

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raise an error for HTTP errors (4xx/5xx)
        return response.json()  # Parse and return the JSON response
    except requests.JSONDecodeError:
        raise ValueError("The response is not valid JSON.")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        raise  # Re-raise the exception for the caller to handle
