from nicegui import ui
from app.modules.ui_elements import create_header
from app.modules.config import Config
from app.modules.login import check_login
import logging
import requests

logger = logging.getLogger(__name__)


class About:
    def __init__(self): ...

    @ui.page("/about")
    def help_about(self):
        try:
            if not check_login():
                return

            create_header()  # Add the header to the page

            with ui.column().classes(
                "w-full items-center p-4 gap-4"
            ):  # Center the content with padding and spacing

                # About section
                with ui.card().classes("w-full max-w-screen-md p-4"):
                    ui.image("/static/icon_full.png").classes(
                        "w-32 h-32 mx-auto"
                    )  # Centered image with specified size
                    ui.markdown("# About WhisperNet").classes("text-center")
                    ui.markdown(
                        """
                    WhisperNet is an offensive cybersecurity platform designed to streamline C2 operations.
                    It integrates powerful tools and automation to assist red teams in executing quiet, efficient network operations... 
                    or at least that's the goal. It's not quite done yet :)
                    """
                    )

                # Help section
                with ui.card().classes("w-full max-w-screen-md p-4"):
                    ui.markdown("# Help & Documentation").classes("text-center")
                    with ui.column().classes("gap-2"):
                        ui.markdown("[Documentation Link](#)").classes(
                            "text-lg text-blue-500"
                        )
                        ui.markdown(
                            "[GitHub Page](https://github.com/ryanq47/WhisperNet-Offensive)"
                        ).classes("text-lg text-blue-500")
                        ui.markdown(
                            "[Submit a Problem](https://github.com/ryanq47/WhisperNet-Offensive/issues)"
                        ).classes("text-lg text-blue-500")
                        ui.markdown(
                            """
                        If you need additional support, please visit the documentation or submit a problem on our issue tracker.
                        You can also check out our GitHub page for the latest updates and contributions.
                        """
                        )

        except Exception as e:
            logger.error(e)
            raise e
