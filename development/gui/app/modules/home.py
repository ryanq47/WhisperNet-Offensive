from nicegui import ui
from app.modules.ui_elements import create_header
import logging

logger = logging.getLogger(__name__)

def homepage():
    try:
        create_header()  # Add the header to the page
        ui.markdown("Whispernet-Offensive Client")

        #ui.button('Click me', on_click=hello)
    except Exception as e:
        logger.error(e)
        raise e