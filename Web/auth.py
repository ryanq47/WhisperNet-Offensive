from nicegui import ui, app
from config import Config
import requests
import re

# from networking import api_call


class AuthView:
    def __init__(self):
        self.username = None
        self.password = None

    def render(self):
        with ui.column().classes(
            "items-center justify-center absolute-center w-full h-screen bg-neutral-100"
        ):
            with ui.card().classes("w-full max-w-sm p-4 shadow-lg bg-white"):
                ui.label("Login").classes(
                    "text-2xl font-bold text-center text-slate-600 mb-4"
                )
                ui.separator().classes("mb-4")

                with ui.column().classes("gap-4"):
                    self.username = (
                        ui.input("Username").props("outlined").classes("w-full")
                    )
                    self.password = (
                        ui.input("Password", password=True)
                        .props("outlined")
                        .classes("w-full")
                    ).on(
                        "keydown.enter",
                        lambda e: ui.notification(
                            self.authenticate()
                        ),  # login(username_input.value, password_input.value),
                    )
                    ui.button("Login", on_click=self.authenticate).classes(
                        "bg-blue-500 text-white w-full hover:bg-blue-600"
                    )

                ui.link("Forgot Password?", "/forgot-password").classes(
                    f"text-sm text-slate-500 mt-4"
                )

    def authenticate(self):
        username = self.username.value
        password = self.password.value

        if self.auth_api_call():
            ui.navigate.to("/")
        else:
            ui.notify("Invalid username or password", type="negative")

    def auth_api_call(self):
        data = {"username": self.username.value, "password": self.password.value}

        r = requests.post(url=f"{Config.API_HOST}/auth/login", json=data)

        access_token = r.json().get("data", {}).get("access_token", {})

        if is_valid_jwt(access_token):
            store_token(token=access_token)
            # print(access_token)
            ui.notify("success")
            return True

        return False


def is_valid_jwt(token):
    jwt_regex = r"^[A-Za-z0-9-_]+?\.[A-Za-z0-9-_]+\.([A-Za-z0-9-_]+)?$"
    return re.match(jwt_regex, token) is not None


def store_token(token: str):
    app.storage.user["jwt_token"] = token


def retrieve_token():
    return app.storage.user.get("jwt_token")
