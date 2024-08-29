from nicegui import ui
from app.modules.ui_elements import create_header
import logging

logger = logging.getLogger(__name__)


def homepage():
    try:
        create_header()  # Add the header to the page
        ui.markdown("# Whispernet-Offensive Client")

        # Create a container for the grid layout
        with ui.row().classes('grid grid-cols-2 gap-4 w-full p-4'):  # 2 columns grid with gaps
            # First card
            with ui.card().classes('w-full p-4'):  # Full width within its grid column
                ui.markdown("### Card1")
                ui.markdown("STUFF")

            # Second card
            with ui.card().classes('w-full p-4'):  # Full width within its grid column
                ui.markdown("### Card2")
                ui.markdown("STUFF")

            # Third card
            with ui.card().classes('w-full p-4'):  # Full width within its grid column
                ui.markdown("### Card3")
                ui.markdown("STUFF")

            # Fourth card
            with ui.card().classes('w-full p-4'):  # Full width within its grid column
                ui.markdown("### Card4")
                ui.markdown("STUFF")

    except Exception as e:
        logger.error(e)
        raise e