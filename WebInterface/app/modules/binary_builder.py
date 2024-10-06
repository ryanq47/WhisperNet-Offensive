from nicegui import ui
from app.modules.ui_elements import create_header
from app.modules.config import Config
from app.modules.login import check_login
import logging

logger = logging.getLogger(__name__)

def fetch_binaries():
    # Static data for testing
    return [
        {'name': 'Binary A'},
        {'name': 'Binary B'},
        {'name': 'Binary C'},
        {'name': 'Binary D'},
    ]

@ui.page('/binary-builder')
def help_about():
    try:
        if not check_login():
            return

        create_header()  # Add the header to the page

        ui.markdown("# Binary Builder")

        # Fetch binaries from the static function
        binaries = fetch_binaries()

        # Create variables to hold user input


        # Create layout
        with ui.card().style('padding: 20px; max-width: 500px; margin: auto;'):
            # Dropdown button for selecting binary
            with ui.dropdown_button('Select a Binary', auto_close=True):
                for binary in binaries:
                    ui.item(binary['name'], on_click=lambda name=binary['name']: on_binary_select(name))

            # Input fields
            ui.input('IP Address', placeholder='Enter IP address')
            ui.input('Port', placeholder='Enter port')
            ui.input('Binary Name', placeholder='Enter binary name')

            # Download button
            #ui.button('Download', on_click=lambda: download_binary(binary_name.value))

            # Log area
            log_area = ui.textarea().style('height: 200px; width: 100%;').classes('bg-gray-100')

    except Exception as e:
        logger.error(e)
        raise e

def on_binary_select(binary_name):
    # Update the binary name input based on selected binary
    ui.get('binary_name').set_value(binary_name)  # Set Binary Name based on selection

def download_binary(binary_name):
    logger.info(f"Downloading binary: {binary_name}")
    # Implement your binary download logic here
    ui.notify(f'Downloading {binary_name}...')  # Feedback to user

