from nicegui import ui
from config import ThemeConfig


class AboutView:
    def __init__(self):
        pass

    def render(self):
        try:
            with ui.row().classes("w-full h-full items-center justify-center border"):
                with ui.column().classes(
                    "w-full h-full items-center justify-center p-24"
                ):
                    # Image Section
                    ui.image("/static/icon_full.png").classes("w-32 h-32 mx-auto")

                    # Header Section
                    ui.label("About WhisperNet").classes(
                        "text-3xl font-extrabold text-center  800"
                    )

                    # Description Section
                    # ui.label(
                    #     "WhisperNet is an offensive cybersecurity platform designed to streamline C2 operations. It integrates powerful tools and automation to assist red teams in executing quiet, efficient network operations."
                    # ).classes("text-base text-center  600")

                    ui.label(
                        "Some really cool oneliner that explains the platform!!!!"
                    ).classes("text-base text-center  600")

                    # Links Section
                    with ui.column().classes("w-full items-center"):
                        ui.link("Documentation", "#").classes(
                            f"text-lg font-medium text-blue-600 hover:underline {ThemeConfig.link}"
                        )
                        ui.link(
                            "GitHub Page",
                            "https://github.com/ryanq47/WhisperNet-Offensive",
                        ).classes(
                            f"text-lg font-medium text-blue-600 hover:underline {ThemeConfig.link}"
                        )
                        ui.link(
                            "Submit a Problem",
                            "https://github.com/ryanq47/WhisperNet-Offensive/issues",
                        ).classes(
                            f"text-lg font-medium text-blue-600 hover:underline {ThemeConfig.link}"
                        )

        except Exception as e:
            print(e)
            raise e
