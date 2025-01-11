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


# ----------------------------------------------
#               Assets N stuff
# ----------------------------------------------
person = """
404: could not locate page, better go find it...
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

# ui.label("Get a standardized professional error message for not fun mode")


class ErrorPage:

    # ----------------------------------------------
    #               404
    # ----------------------------------------------

    @staticmethod
    @ui.page("/404")
    def http_404():
        navbar()
        current_settings = app.storage.user.get("settings", {})
        if current_settings.get("More Fun Mode", False):
            # Initial position of the walking element
            position = {"left": 0}

            # Function to update position
            def move():
                position["left"] += 10  # Move 10 pixels to the right
                if position["left"] > 1920:  # Reset position after reaching the end
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

        else:
            ui.label("404 Error")

    # ----------------------------------------------
    #               500
    # ----------------------------------------------
    @staticmethod
    @ui.page("/500")
    def http_500():
        navbar()
        current_settings = app.storage.user.get("settings", {})
        if current_settings.get("More Fun Mode", False):
            with ui.element().classes("absolute-center"):
                ui.image("static/youre_did_it.png").props(f"width=400px height=400px")
                ui.label("Good f***ing job, you broke something - 500 error").classes(
                    "flex justify-center items-center"
                )

        else:
            ui.label("500 Error")


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


@app.exception_handler(500)
async def exception_handler_404(request, exception: Exception):
    with Client(page(""), request=request) as client:
        ui.navigate.to("/500")
    return client.build_response(request, 500)
