from nicegui import ui
from app.modules.ui_elements import create_header
from app.modules.config import Config
from app.modules.login import check_login
import logging
import requests
import munch

logger = logging.getLogger(__name__)


def get_targets() -> dict:
    """
    Function to retrieve container data from server.
    """
    try:
        url = Config().get_url() / "binary_builder" / "targets"
        token = Config().get_token()

        headers = {
            'Authorization': f'Bearer {token}'
        }

        logger.debug("Getting containers from server")
        response = requests.get(url, headers=headers, verify=Config().get_verify_certs())

        if response.status_code == 200:
            data = response.json()
            target_data = munch.Munch(data.get("data", {}))
            logger.debug(f"target_data retrieved: {target_data}")
            return target_data
        else:
            logger.warning(f"Received a {response.status_code} status code when requesting {url}")
            return {}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e


from nicegui import ui

# Declare log_area globally
log_area = None

@ui.page('/binary-builder')
def help_about():
    try:
        if not check_login():
            return

        create_header()  # Add the header to the page

        ui.markdown("# Binary Builder")

        # Fetch binaries from the server
        global targets  # Make targets global to access in the callback
        targets = get_targets()

        # Create layout
        with ui.card().classes('w-full p-4 space-y-6'):
            # Dropdown selection for selecting binary
            binary_select = ui.select(
                list({**targets.agents, **targets.droppers}.keys()),  # Combine keys from agents and droppers
                value=None,
            ).bind_value(on_target_select, 'value')  # Bind the selected value to the callback

            # Description section
            with ui.column().classes('w-full max-w-md'):
                ui.markdown("### Description")
                log_area = ui.markdown("Select a binary from the dropdown to proceed.")

            # Input fields
            with ui.row().classes('space-x-4'):
                with ui.column().classes('flex-1'):
                    ip_input = ui.input('IP Address', placeholder='Enter IP address')
                    port_input = ui.input('Port', placeholder='Enter port')
                    binary_input = ui.input('Binary Name', placeholder='Enter binary name')

                with ui.column().classes('max-w-md'):
                    ui.markdown("### Description")
                    ui.markdown("**IP Address:** The address of the target machine.")
                    ui.markdown("**Port:** The port to connect to on the target machine.")
                    ui.markdown("**Binary Name:** The name of the binary to be downloaded.")

    except Exception as e:
        logger.error(e)
        raise e

def on_target_select(selected_name, targets):
    global log_area  # Access the global log_area
    # Initialize description
    description = ""

    # Access descriptions using dictionary key access
    agent_description = targets.agents.get(selected_name, {}).get('description', None)
    dropper_description = targets.droppers.get(selected_name, {}).get('description', None)

    # Set description based on what was found
    if agent_description:
        description = agent_description
    elif dropper_description:
        description = dropper_description
    else:
        description = 'No description available for this target.'

    # Update the description area
    #ui.update(log_area, value=description)



def download_binary(binary_name):
    logger.info(f"Downloading binary: {binary_name}")
    # Implement your binary download logic here
    ui.notify(f'Downloading {binary_name}...')  # Feedback to user

