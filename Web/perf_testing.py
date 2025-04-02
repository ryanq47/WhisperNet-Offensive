import time
from nicegui import app, ui


def api_call_time(func):
    """
    Track the API call time for each api OR function call.

    If call time is greated than .5 seconds, print ui.notify red.

    Else, display call time on screen
    """

    # if app.storage.user.get("settings", {}).get("Display API Call Times"):
    def wrapper(*args, **kwargs):
        start = time.time()  # Use time.time() to get the current time in seconds
        result = func(*args, **kwargs)
        end = time.time()  # Get the time after the function has executed

        total_time = end - start
        print(f"{func.__name__}: {args} {total_time} seconds to execute")

        # settings for showing this on screen or not
        if app.storage.user.get("settings", {}).get("Display API Call Times", False):
            if total_time > 0.5:
                ui.notify(
                    f"{func.__name__}: {args} {end - start} seconds to execute",
                    position="top-right",
                    type="warning",
                )
            else:
                ui.notify(
                    f"{func.__name__}: {args} {end - start} seconds to execute",
                    position="top-right",
                    type="info",
                )

        return result  # Ensure the result of the original function is returned

    return wrapper


def func_call_time(func):
    """
    Track the function call time.

    If call time is greated than .5 seconds, print ui.notify red.

    Else, display call time on screen
    """

    # if app.storage.user.get("settings", {}).get("Display API Call Times"):
    def wrapper(*args, **kwargs):
        start = time.time()  # Use time.time() to get the current time in seconds
        result = func(*args, **kwargs)
        end = time.time()  # Get the time after the function has executed

        total_time = end - start
        print(f"{func.__name__}: {total_time} seconds to execute")

        # settings for showing this on screen or not
        if app.storage.user.get("settings", {}).get(
            "Display Function Call Times", False
        ):
            if total_time > 0.5:
                ui.notify(
                    f"{func.__name__}: {end - start} seconds to execute",
                    position="top-right",
                    type="warning",
                )
            else:
                ui.notify(
                    f"{func.__name__}: {end - start} seconds to execute",
                    position="top-right",
                    type="info",
                )

        return result  # Ensure the result of the original function is returned

    return wrapper
