# Notes on how this works
#
# When imported in main.py, the error handlers get setup.
#
# Each one of those then calls an ErrorPage class object, which is rendered on screen
# perf Hit: On *really* slow browsers, you see the page refresh/redirect to the custom error page
# This is not a problem with stuff outside of a VM/Kali's firefox which is wicked slow for some reason

from nicegui import ui, Client, app
from nicegui.page import page
import math
from navbar import navbar
from auth import check_login

# ----------------------------------------------
#               Assets N stuff
# ----------------------------------------------
person = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⡈⠛⢉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⢿⣿⣿⣿⣿⣿⠀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢰⣿⡏⠀⢸⣿⣿⣿⣿⡇⢸⣷⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣼⣿⠁⠀⢸⣿⣿⣿⣿⠁⠀⠙⠻⢿⣿⣶⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠛⠋⠀⠀⠸⣿⣿⣿⡏⠀⠀⠀⠀⠀⠈⠉⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣄⠙⣿⣿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣦⠈⢿⣿⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⡟⠀⠀⠻⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⠟⠁⠀⠀⠀⠘⢿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢾⣿⠟⠁⠀⠀⠀⠀⠀⠀⠈⢻⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀

              """


class ErrorPage:

    # ----------------------------------------------
    #               404
    # ----------------------------------------------

    @staticmethod
    @ui.page("/404")
    def http_404():
        check_login()
        with navbar():
            current_settings = app.storage.user.get("settings", {})
            # Have to include this so error message gets centered
            with ui.column().classes("w-full h-full items-center justify-center"):
                if current_settings.get("More Fun Mode", False):
                    # Initial position of the walking element
                    position = {"left": 0}

                    # Function to update position
                    def move():
                        position["left"] += 10  # Move 10 pixels to the right
                        if (
                            position["left"] > 1920
                        ):  # Reset position after reaching the end
                            position["left"] = 0
                        walking_element.style(
                            f"position: absolute; left: {position['left']}px;"
                        )

                    # Create the walking element
                    with ui.row().style("position: relative; height: 100px;"):
                        walking_element = ui.label(person).style(
                            "position: absolute; left: 0px;"
                        )

                    # Timer to trigger the move function
                    ui.timer(interval=0.1, callback=move)  # Update position every 100ms
                    error_box(
                        status_code="404",
                        error_message="could not locate page, better keep looking...",
                    )

                else:
                    error_box(status_code="404", error_message="Page not found")

    # ----------------------------------------------
    #               404
    # ----------------------------------------------

    @staticmethod
    @ui.page("/401")
    def http_401():
        current_settings = app.storage.user.get("settings", {})

        with navbar():

            if current_settings.get("More Fun Mode", False):
                ui.notify(
                    "Token has expired, please log in again.", position="top-right"
                )

            else:
                ui.notify(
                    "Token has expired, please log in again.", position="top-right"
                )

            ui.navigate.to("/auth")

    # ----------------------------------------------
    #               500
    # ----------------------------------------------
    @staticmethod
    @ui.page("/500")
    def http_500():
        check_login()
        with navbar():
            with ui.column().classes("w-full h-full items-center justify-center"):
                current_settings = app.storage.user.get("settings", {})
                if current_settings.get("More Fun Mode", False):
                    ui.image("static/youre_did_it.png").props(
                        f"width=400px height=400px"
                    )

                    error_box(
                        status_code="500",
                        error_message="Good f**ing job, you broke something",
                    )

                else:
                    ui.label("500 Error")

                    error_box(status_code="500", error_message="Server Error")


# ----------------------------------------------
#               Helper Functions
# ----------------------------------------------


def error_box(status_code, error_message):
    """Error box for easier error formatting

    Args:
        status_code (string): The status code
        error_message (string): The message for the error box
    """
    ui.markdown(f"# {status_code} - {error_message}")


# ----------------------------------------------
#               Exception Handlers
# ----------------------------------------------

## Addtl ideas:
# 401, unauth. Keyhole with wrong key?


@app.exception_handler(404)
async def exception_handler_404(request, exception: Exception):
    with Client(page(""), request=request) as client:
        ui.navigate.to("/404")
    return client.build_response(request, 404)


@app.exception_handler(401)
async def exception_handler_401(request, exception: Exception):
    with Client(page(""), request=request) as client:
        ui.navigate.to("/401")
    return client.build_response(request, 401)


@app.exception_handler(500)
async def exception_handler_404(request, exception: Exception):
    with Client(page(""), request=request) as client:
        ui.navigate.to("/500")
    return client.build_response(request, 500)
