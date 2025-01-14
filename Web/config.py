from nicegui import app

# # Load settings from session storage or use defaults
# current_settings = app.storage.user.get("settings")

# # Apply dark mode based on the setting
# DARK_MODE = current_settings.get("Dark Mode")


class ThemeConfig:
    link = "underline"  #  600 hover: 800 visited: 600"
    # dark_link = "underline text-green-600 hover:text-green-800 visited:text-green-600"
    gap = ""  # "gap-1"  # gap between elements


class Config:
    API_HOST = None  # Initialize to None or a default value

    @staticmethod
    def set_api_host(host: str):
        ThemeConfig.API_HOST = host

    @staticmethod
    def get_api_host() -> str:
        if not ThemeConfig.API_HOST:
            raise ValueError("API host is not set.")
        return ThemeConfig.API_HOST
