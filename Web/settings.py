from nicegui import ui, app
import requests
from config import Config


class Settings:
    def __init__(self):
        pass

    def render(self):
        current_settings = app.storage.user.get("settings", {})

        with ui.tabs() as tabs:
            ui.tab("LOCAL SETTINGS")
            ui.tab("USERS")

        with ui.tab_panels(tabs, value="LOCAL SETTINGS").classes("w-full border"):
            with ui.tab_panel("LOCAL SETTINGS"):
                # ui.label('Content of A')
                ls = LocalSettings()
                ls.render()
            if current_settings.get("Dev Mode", False):
                with ui.tab_panel("USERS"):
                    u = Users()
                    u.render()
                # ls = LocalSettings()
                # ls.render()


## HEY - FINISH THE REGISTER USER and make it pretty


from nicegui import ui
import requests


class Users:
    def __init__(self):
        self.user_data = []  # Store user data for the table
        self.user_table = None  # Placeholder for the table

    def render(self):
        with ui.tabs() as tabs:
            ui.tab("REGISTER")
            ui.tab("USER LIST")

        with ui.tab_panels(tabs, value="REGISTER").classes("w-full"):
            # Tab for registering users
            with ui.tab_panel("REGISTER"):
                self.register_user_view()

            # Tab for listing users
            with ui.tab_panel("USER LIST"):
                self.list_users_view()

    def register_user_view(self):
        """
        Render the user registration view.
        """
        with ui.column().classes("items-center justify-center w-full"):
            ui.label("Register a user").classes("text-2xl font-bold text-center mb-4")
            ui.separator().classes("mb-4")

            # Input fields and register button
            with ui.column().classes("gap-4 w-1/2 max-w-md"):
                self.username_input = (
                    ui.input("Username").props("outlined").classes("w-full")
                )
                self.password_input = (
                    ui.input("Password", password=True, password_toggle_button=True)
                    .props("outlined")
                    .classes("w-full")
                )
                ui.button("Register User", on_click=self.register_api_call).classes(
                    "bg-blue-500 text-white w-full hover:bg-blue-600 rounded-lg"
                )

    def register_api_call(self):
        """
        Register a new user via the API.
        """
        data = {
            "username": self.username_input.value,
            "password": self.password_input.value,
        }

        headers = {
            "Authorization": f"Bearer {app.storage.user.get("jwt_token", "")}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                url=f"{Config.API_HOST}/auth/register", json=data, headers=headers
            )

            if response.status_code == 201:
                ui.notify(
                    f"User '{self.username_input.value}' created successfully",
                    type="positive",
                )
                self.load_users()  # Refresh the user list after registration
            else:
                ui.notify(
                    f"Error registering user: {response.status_code}", type="warning"
                )
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")

    def list_users_view(self):
        """
        Render the user list view.
        """
        current_settings = app.storage.user.get("settings", {})
        # auto load users on tab creation
        # self.load_users()
        with ui.column().classes("w-full items-center justify-center"):
            ui.label("User Management").classes("text-2xl font-bold text-center mb-4")
            ui.separator().classes("mb-4")

            aggrid_theme = (
                "ag-theme-balham-dark"
                if current_settings.get("Dark Mode", False)
                else "ag-theme-balham"
            )

            # Add table for user management
            self.user_table = ui.aggrid(
                {
                    "columnDefs": [
                        {
                            "headerName": "UUID",
                            "field": "uuid",
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                        },
                        {
                            "headerName": "Username",
                            "field": "username",
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                        },
                    ],
                    "rowData": self.user_data,
                    "enableCellTextSelection": True,  # allows selecting data
                }
            ).classes(f"w-full {aggrid_theme}")

            # Button to refresh the table
            ui.button("Refresh Users", on_click=self.load_users).classes(
                "bg-green-500 text-white mt-4 hover:bg-green-600"
            )

    def load_users(self):
        """
        Fetch users from the /auth/users endpoint and update the table.
        """
        try:
            headers = {
                "Authorization": f"Bearer {app.storage.user.get("jwt_token", "")}",
                "Content-Type": "application/json",
            }
            response = requests.get(
                url=f"{Config.API_HOST}/auth/users", headers=headers
            )
            if response.status_code == 200:
                self.user_data = response.json().get("data", {}).get("users", [])
                self.user_table.options["rowData"] = self.user_data
                self.user_table.update()  # Refresh the table with new data
                ui.notify("User list updated successfully", type="positive")
            else:
                ui.notify(
                    f"Failed to load users: {response.status_code}", type="warning"
                )
        except Exception as e:
            ui.notify(f"Error loading users: {e}", type="negative")


class LocalSettings:
    def __init__(self):
        # Default settings: each setting has a value and a description
        self.default_settings = {
            "Dark Mode": {
                "value": False,
                "description": "Switch between a light and dark theme",
            },
            "More Fun Mode": {
                "value": False,
                "description": "Add extra excitement to the UI",
            },
            "Dev Mode": {
                "value": False,
                "description": "Enable features under development",
            },
        }

    def render(self):
        # ui.label("A clear settings button would be nice")
        try:
            # Load settings from session storage or use defaults
            current_settings = app.storage.user.get("settings", self.default_settings)

            with ui.column().classes("w-full items-center p-4 gap-4"):
                # Page Header
                ui.markdown("# Settings").classes("text-center text-2xl")

                # Settings Toggles
                for setting_name, setting_data in current_settings.items():
                    with ui.row().classes("justify-between w-full max-w-screen-md"):
                        with ui.column():
                            ui.label(setting_name).classes("text-lg")
                            ui.label(setting_data["description"]).classes(
                                "text-sm text-gray-500"
                            )
                        ui.switch(value=setting_data["value"]).bind_value(
                            current_settings[setting_name], "value"
                        )

                # Save and Clear Buttons
                with ui.row().classes("gap-4"):
                    ui.button(
                        "Clear Local Settings", on_click=self.clear_settings
                    ).classes(
                        "mt-4 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
                    )

                    ui.button(
                        "Save",
                        on_click=lambda: self.save_settings(current_settings),
                    ).classes(
                        "mt-4 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
                    )

        except Exception as e:
            print(f"Error rendering settings page: {e}")

    def save_settings(self, current_settings):
        # Save settings to session storage
        app.storage.user["settings"] = current_settings
        ui.notify("Settings saved! Refresh to take effect")

    def clear_settings(self):
        # Completely clear user settings from session storage
        app.storage.user.clear()
        ui.notify("Settings cleared! Next load will use defaults")

    @staticmethod
    def apply_settings():
        # Load settings from session storage
        current_settings = app.storage.user.get("settings", {})

        # 1) Force "Dark Mode" to be a dictionary if it isn't already
        if isinstance(current_settings.get("Dark Mode"), bool):
            dark_mode_value = current_settings["Dark Mode"]
            # Overwrite with proper dictionary structure
            current_settings["Dark Mode"] = {
                "value": dark_mode_value,
                "description": "Switch between a light and dark theme",
            }
            # Save it back so next time it won't break
            app.storage.user["settings"] = current_settings

        # 2) Now we can safely check 'Dark Mode' as a dictionary
        if current_settings.get("Dark Mode", {}).get("value"):
            ui.dark_mode().enable()
        else:
            ui.dark_mode().disable()
