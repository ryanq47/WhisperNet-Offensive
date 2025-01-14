from nicegui import ui, app


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


class Users:
    def __init__(self):
        pass

    def render(self):
        with ui.tabs() as tabs:
            ui.tab("REGISTER")
            ui.tab("OTHER TABS")

        with ui.tab_panels(tabs, value="REGISTER").classes("w-full border"):
            with ui.tab_panel("REGISTER"):
                # ui.label('Content of A')
                # ls = LocalSettings()
                # ls.render()
                self.register_user_view()
            # with ui.tab_panel("USERS"):
            #     ui.label("Content of USERS")
            #     # ls = LocalSettings()
            #     # ls.render()

    def register_user_view(self):
        with ui.column().classes("items-center justify-center w-full"):
            ui.label("Register a user").classes(
                "text-2xl font-bold text-center text-slate-600 mb-4"
            )
            ui.separator().classes("mb-4")

            # Input fields and login button
            with ui.column().classes("gap-4 w-1/2 max-w-md"):  # Limit maximum width
                self.username = ui.input("Username").props("outlined").classes("w-full")
                self.password = (
                    ui.input("Password", password=True, password_toggle_button=True)
                    .props("outlined")
                    .classes("w-full")
                )
                ui.button("Register User").classes(
                    "bg-blue-500 text-white w-full hover:bg-blue-600 rounded-lg"
                )


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
