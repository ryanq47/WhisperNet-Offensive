from nicegui import ui, app


# bug, first load, these do not save
class Settings:
    def __init__(self):
        # Default settings
        self.default_settings = {
            "Dark Mode": False,
            "More Fun Mode": False,
            # "Enable Notifications": True,
            # "Auto Update": True,
            # "Debug Mode": False,
        }

    def render(self):
        ui.label("A clear settings button would be nice")
        try:
            # Load settings from session storage or use defaults
            current_settings = app.storage.user.get("settings", self.default_settings)

            with ui.column().classes("w-full items-center p-4 gap-4"):
                # Page Header
                ui.markdown("# Settings").classes("text-center text-2xl")

                # Settings Toggles
                for setting, value in current_settings.items():
                    with ui.row().classes("justify-between w-full max-w-screen-md"):
                        ui.label(setting).classes("text-lg")
                        ui.switch(value=value).bind_value(current_settings, setting)

                # Save Button
                ui.button(
                    "Save", on_click=lambda: self.save_settings(current_settings)
                ).classes(
                    "mt-4 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
                )
        except Exception as e:
            print(f"Error rendering settings page: {e}")

    def save_settings(self, current_settings):
        # Save settings to session storage
        app.storage.user["settings"] = current_settings
        ui.notify("Settings saved! Refresh to take effect")

    # called from outside of this class, meant to apply settings.
    # called in the navbar to apply settings if needed
    @staticmethod
    def apply_settings():

        # Dark Mode Setting
        # Load settings from session storage
        current_settings = app.storage.user.get("settings", {"Dark Mode": False})

        # Apply dark mode if enabled
        if current_settings.get("Dark Mode"):
            ui.dark_mode().enable()
