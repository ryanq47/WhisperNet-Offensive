from nicegui import ui
from app.modules.ui_elements import create_header
from app.modules.config import Config
from app.modules.login import check_login
import logging
import requests
import munch
from app.modules.utils import is_base64

logger = logging.getLogger(__name__)

# Placeholder for targets data
targets = {}

def get_targets() -> dict:
    """
    Function to retrieve container data from the server.
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

def on_target_select(selected_name):
    """
    Callback function to update the description, header, language, and display the shellcode field if a custom is selected.
    """
    # Access descriptions and language using dictionary key access
    agent = targets.agents.get(selected_name)
    dropper = targets.droppers.get(selected_name)
    custom = targets.customs.get(selected_name)
    
    # Initialize variables for description and language
    description = "No description available for this target."
    language = "Unknown"

    # Set description and language based on what was found
    if agent:
        description = agent.get('description', description)
        language = agent.get('language', language)
        shellcode_input.visible = False  # Hide shellcode input if it's an agent
        ip_input.visible = True
        port_input.visible = True
        binary_name_input.visible = True

    elif dropper:
        description = dropper.get('description', description)
        language = dropper.get('language', language)
        shellcode_input.visible = False  # Hide shellcode input if it's an agent
        ip_input.visible = True
        port_input.visible = True
        binary_name_input.visible = True

    elif custom:
        description = custom.get('description', description)
        language = custom.get('language', language)
        shellcode_input.visible = True  # Show shellcode input field if it's a custom
        ip_input.visible = False
        port_input.visible = False
        binary_name_input.visible = True


    else:
        shellcode_input.visible = False  # Hide shellcode input if not a custom

    # Escape underscores in the selected name
    escaped_name = selected_name.replace('_', '\\_')

    # Update the description text, header, and language dynamically
    description_header.set_content(f"### {escaped_name}")
    description_text.set_content(description)
    language_text.set_content(f"Language: {language}")


@ui.page('/binary-builder')
def binary_builder_page():
    """
    Main UI page for Binary Builder.
    """
    try:
        if not check_login():
            return

        create_header()  # Add the header to the page


         # Make necessary elements global for update access
        global targets, shellcode_input, description_text, description_header, language_text , ip_input, port_input, binary_name_input
        
        # Fetch binaries from the server
        targets = get_targets()


        # Create layout
        with ui.card().classes('w-full h-[93vh] flex flex-col'):
            ui.markdown("# Binary Builder")

            # Initialize description area
            description_header = ui.markdown("### Select a binary")
            description_text = ui.markdown("Select a binary from the dropdown to proceed.")
            language_text = ui.markdown(f"Language: ")

            # Dropdown selection for selecting binary
            binary_select = ui.select(
                list({**targets.agents, **targets.customs, **targets.droppers}.keys()),  # Combine keys from agents and customs
                value=None,
                label="Select a binary",
                on_change=lambda e: on_target_select(e.value)  # Call on_target_select on change
            )

            # Input fields for additional binary configuration
            with ui.row().classes('space-x-4'):
                ip_input = ui.input('IP Address', placeholder='Enter IP address')
                port_input = ui.input('Port', placeholder='Enter port')
                binary_name_input = ui.input('Binary Name', placeholder='Enter binary name')

            # Shellcode input (hidden by default, only visible for customs)
            # can do an on_changed to validate input as well.
            shellcode_input = ui.textarea(label='Shellcode (base64 please)', placeholder='Enter shellcode here', on_change=lambda e:validate_shellcode(e.value)).classes('w-full').props('autogrow').props('clearable')
            shellcode_input.visible = False  # Set initial visibility to False

            # Download button
            ui.button('Download Binary', on_click=lambda: download_binary(binary_name_input.value)).classes('mt-4')

    except Exception as e:
        logger.error(e)
        raise e

def validate_shellcode(b64_shellcode):
    if not is_base64(b64_shellcode):
        ui.notify("Shellcode is seemingly not base64!", type="warning")


def download_binary(binary_name):
    """
    Function to handle downloading the selected binary.
    """
    logger.info(f"Downloading binary: {binary_name}")
    # Implement your binary download logic here
    ui.notify(f'Downloading {binary_name}...')  # Feedback to the user
