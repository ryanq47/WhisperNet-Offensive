from functools import wraps
from nicegui import app, ui
from config import Config
import requests
import re

jwt_regex = r"^[A-Za-z0-9-_]+?\.[A-Za-z0-9-_]+\.([A-Za-z0-9-_]+)?$"


class AuthView:
    def __init__(self):
        self.username = None
        self.password = None
        self.api_host = None  # url of server, full thing + protocol

    def render(self):
        # Clear user-specific session data on load of auth page
        # Doing this as a failsafe for dev, and if any session data gets left in there
        app.storage.user.clear()
        add_particles_background()
        ui.page_title("HCKD")

        with ui.column().classes(
            "items-center justify-center absolute-center w-full h-screen"
        ):
            with ui.card().classes("w-full max-w-sm p-6 shadow-lg"):
                ui.label("Login").classes(
                    "text-2xl font-bold text-center text-slate-600 mb-4"
                )
                ui.markdown(
                    "API address is set at run time, with the `--api-host` argument"
                )
                ui.separator().classes("mb-4")

                # Input fields and login button
                with ui.column().classes("gap-4 w-full"):
                    # self.api_host = (
                    #     ui.input("Server", placeholder="http(s)://<address>:<port>")
                    #     .props("outlined")
                    #     .classes("w-full")
                    # )
                    # Config.set_api_host(host=self.api_host.value)

                    self.username = (
                        ui.input("Username").props("outlined").classes("w-full")
                    )
                    self.password = (
                        ui.input("Password", password=True, password_toggle_button=True)
                        .props("outlined")
                        .classes("w-full")
                    ).on(
                        "keydown.enter",
                        lambda e: ui.notification(self.authenticate()),
                    )

                    ui.button("Login", on_click=self.authenticate).classes(
                        "bg-blue-500 text-white w-full hover:bg-blue-600 rounded-lg"
                    )

                # # Forgot password link centered below the form
                # ui.link("Forgot Password?", "/forgot-password").classes(
                #     "text-sm text-slate-500 mt-4 text-center"
                # )

    def authenticate(self):
        username = self.username.value
        password = self.password.value

        if self.auth_api_call():
            ui.navigate.to("/")
        else:
            ui.notify(
                "Invalid username or password", type="negative", position="top-right"
            )

    def auth_api_call(self):
        data = {"username": self.username.value, "password": self.password.value}

        r = requests.post(url=f"{Config.API_HOST}/auth/login", json=data)

        access_token = r.json().get("data", {}).get("access_token", {})

        if is_valid_jwt(access_token):
            store_token(token=access_token)
            store_user(username=self.username.value)
            # print(access_token)
            ui.notify("success", position="top-right")
            return True

        return False


@ui.page("/logout")
def logout():
    check_login()
    app.storage.user.clear()  # Clear user-specific session data
    ui.notify("Logged out successfully", type="positive", position="top-right")
    ui.navigate.to("/auth")


def is_valid_jwt(token):
    # default to false if it's empty
    if token == "" or token == None:
        return False
    # returns true
    return re.match(jwt_regex, token) is not None


def store_token(token: str):
    app.storage.user["jwt_token"] = token


def store_user(username: str):
    app.storage.user["username"] = username


def retrieve_token():
    return app.storage.user.get("jwt_token")


def check_login():
    jwt = app.storage.user.get("jwt_token")
    if is_valid_jwt(jwt):
        return True
    else:
        ui.notify(
            "Please log in to access this page", type="negative", position="top-right"
        )
        ui.navigate.to("/auth")


# @ui.page("/particles")
# bug cuz not being displayed in login page. prolly something with css in the login func
def add_particles_background():
    # Add the particles.js container and load the existing configuration
    ui.add_body_html(
        """
    <div id="particles-js" style="position: fixed; width: 100%; height: 100%; z-index: -1;"></div>
    <script src="/static/particles.js"></script>
    <script>
        // Load particles.js with your existing configuration
        particlesJS.load('particles-js', '/static/particlesjs-config.json', function() {
            console.log('particles.js loaded - callback');
        });
    </script>
    """
    )
