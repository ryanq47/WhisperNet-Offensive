from nicegui import ui
from app.modules.ui_elements import create_header
from app.modules.config import Config
import logging

logger = logging.getLogger(__name__)

ui.add_head_html('<style>body { background-color: #EDEDED; }</style>')

def homepage():
    try:
        create_header()  # Add the header to the page
        ui.markdown("# Whispernet-Offensive Client")



        # Create a container for the grid layout
        with ui.row().classes('grid grid-cols-3 gap-4 w-full h-screen p-4'):  # 3 columns grid with gaps, full height screen
            for i in range(1, 10):  # Adjust the range for the number of cards you want
                
                # manually define these to add unique content, etc
                with ui.card().classes('w-full h-full p-4'):  # Full width and height within its grid column
                    ui.markdown(f"### Card {i}")
                    ui.markdown("STUFF")

    except Exception as e:
        logger.error(e)
        raise e