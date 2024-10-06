import base64
import re

def is_base64(s: str) -> bool:
    """
    Verifies if a given string is valid Base64 encoded.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string is valid Base64, False otherwise.
    """
    # Base64 strings should be a multiple of 4
    if len(s) % 4 != 0:
        return False

    # Use regex to check if the string only contains valid Base64 characters
    if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', s):
        return False

    # Attempt decoding
    try:
        # Decode and re-encode to verify that the string is valid Base64
        return base64.b64encode(base64.b64decode(s)).decode('utf-8') == s
    except Exception:
        return False
