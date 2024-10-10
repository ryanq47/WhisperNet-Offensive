import logging
from pathlib import Path

import munch
import requests
from app.modules.config import Config
from app.modules.login import check_login
from app.modules.ui_elements import create_header
from app.modules.utils import is_base64
from nicegui import ui

logger = logging.getLogger(__name__)

# Placeholder for targets data
targets = {}


def get_targets() -> dict:
    """
    Function to retrieve container data from the server.
    """
    try:
        url = Config().get_url() / "binary-builder" / "targets"
        token = Config().get_token()

        headers = {"Authorization": f"Bearer {token}"}

        logger.debug("Getting containers from server")
        response = requests.get(
            url, headers=headers, verify=Config().get_verify_certs()
        )

        if response.status_code == 200:
            data = response.json()
            target_data = munch.Munch(data.get("data", {}))
            logger.debug(f"target_data retrieved: {target_data}")
            return target_data
        else:
            logger.warning(
                f"Received a {response.status_code} status code when requesting {url}"
            )
            return {}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e


def get_binaries() -> dict:
    """
    Function to retrieve container data from the server.
    """
    try:
        url = Config().get_url() / "binary-builder" / "binaries"
        token = Config().get_token()

        headers = {"Authorization": f"Bearer {token}"}

        logger.debug("Getting containers from server")
        response = requests.get(
            url, headers=headers, verify=Config().get_verify_certs()
        )

        if response.status_code == 200:
            data = response.json()
            target_data = munch.Munch(data.get("data", {}))
            logger.debug(f"target_data retrieved: {target_data}")
            return target_data
        else:
            logger.warning(
                f"Received a {response.status_code} status code when requesting {url}"
            )
            return {}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e


def download_binary(filename):
    """
    Function to download a binary from the Flask API and serve it to the user via NiceGUI.
    """
    try:
        # Construct the Flask API URL for downloading
        url = str(Config().get_url() / "binary-builder" / "binaries" / filename)
        token = Config().get_token()

        headers = {"Authorization": f"Bearer {token}"}

        # Fetch the file from the Flask API
        response = requests.get(
            url, headers=headers, stream=True, verify=Config().get_verify_certs()
        )
        if response.status_code != 200:
            ui.notify(
                f"Failed to download {filename}: {response.status_code}",
                type="negative",
            )
            logger.error(f"Failed to download {filename}: {response.status_code}")
            return

        # Save the file temporarily
        temp_dir = Path("temp_download")
        temp_dir.mkdir(parents=True, exist_ok=True)
        file_path = temp_dir / filename
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Trigger download in NiceGUI to serve it to the client
        ui.download(str(file_path), filename=filename)
        ui.notify(f"Downloading {filename}...")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        ui.notify(f"An error occurred: {e}", type="negative")
        raise e


# Queue compilation function
def queue_compilation():

    if selected_type == "agent":
        queue_agent_compilation(
            target=binary_select.value,
            binary_name=binary_name_input.value,
            ip=ip_input.value,
            port=port_input.value,
        )
    elif selected_type == "dropper":
        queue_dropper_compilation(
            target=binary_select.value,
            binary_name=binary_name_input.value,
            ip=ip_input.value,
            port=port_input.value,
        )
    elif selected_type == "custom":
        queue_custom_compilation(
            target=binary_select.value,
            shellcode=shellcode_input.value,
            binary_name=binary_name_input.value,
        )
    else:
        ui.notify("Please select a valid binary type.")


def queue_agent_compilation(target, binary_name, ip, port):
    """
    Function to queue compilation for an agent.
    """
    # Agent-specific endpoint
    url = Config().get_url() / "binary-builder" / "build" / "agent"
    # Your agent-specific logic here
    return send_compilation_request(
        url, {"target": target, "binary_name": binary_name, "ip": ip, "port": port}
    )


def queue_dropper_compilation(target, binary_name, ip, port):
    """
    Function to queue compilation for a dropper.
    """
    # Dropper-specific endpoint
    url = Config().get_url() / "binary-builder" / "build" / "dropper"
    # Your dropper-specific logic here
    return send_compilation_request(
        url, {"target": target, "binary_name": binary_name, "ip": ip, "port": port}
    )


def queue_custom_compilation(target, binary_name, shellcode):
    """
    Function to queue compilation for a dropper.
    """
    # Dropper-specific endpoint
    url = Config().get_url() / "binary-builder" / "build" / "custom"
    # Your dropper-specific logic here
    return send_compilation_request(
        url, {"target": target, "binary_name": binary_name, "shellcode": shellcode}
    )


def send_compilation_request(url, data):
    """
    Sends a compilation request to the server.
    """
    token = Config().get_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(
        url, headers=headers, json=data, verify=Config().get_verify_certs()
    )
    if response.status_code == 200:
        return True
    else:
        logger.warning(
            f"Compilation request failed with status {response.status_code} for {url}"
        )
        return False


# Adjust the `on_target_select` to store the type (e.g., 'agent', 'dropper', 'custom')
selected_type = None


def on_target_select(selected_name):
    global selected_type  # Store the type of the selected target

    # Access descriptions and language using dictionary key access
    agent = targets.agents.get(selected_name)
    dropper = targets.droppers.get(selected_name)
    custom = targets.customs.get(selected_name)

    # Set the selected type and show/hide input fields accordingly
    if agent:
        selected_type = "agent"
        shellcode_input.visible = False
    elif dropper:
        selected_type = "dropper"
        shellcode_input.visible = False
    elif custom:
        selected_type = "custom"
        shellcode_input.visible = True
    else:
        selected_type = None

    # Update UI elements with the selected target's information
    description_header.set_content(f"### {selected_name.replace('_', '\\_')}")
    description_text.set_content(
        agent.get("description")
        if agent
        else (dropper.get("description") if dropper else custom.get("description"))
    )
    language_text.set_content(
        f"Language: {agent.get('language') if agent else (dropper.get('language') if dropper else custom.get('language'))}"
    )


@ui.page("/binary-builder")
def binary_builder_page():
    try:
        if not check_login():
            return

        create_header()  # Add the header to the page

        # Make necessary elements global for update access
        global targets, shellcode_input, description_text, description_header, language_text, ip_input, port_input, binary_name_input, binary_select

        # Fetch binaries from the server
        targets = get_targets()

        # Main layout with two side-by-side cards
        with ui.row().classes("w-full h-[93vh] flex"):
            # Left card (85% width)
            with ui.card().classes("flex-1 h-full flex flex-col"):
                ui.markdown("# Binary Builder")

                # Initialize description area
                description_header = ui.markdown("### Select a binary")
                description_text = ui.markdown(
                    "Select a binary from the dropdown to proceed."
                )
                language_text = ui.markdown(f"Language: ")

                # Dropdown selection for selecting binary
                binary_select = ui.select(
                    list(
                        {**targets.agents, **targets.customs, **targets.droppers}.keys()
                    ),
                    value=None,
                    label="Select a binary",
                    on_change=lambda e: on_target_select(e.value),
                )

                # Input fields for additional binary configuration
                with ui.row().classes("space-x-4"):
                    ip_input = ui.input("IP Address", placeholder="Enter IP address")
                    port_input = ui.input("Port", placeholder="Enter port")
                    binary_name_input = ui.input(
                        "Binary Name", placeholder="Enter binary name"
                    )

                # Shellcode input (hidden by default, only visible for customs)
                shellcode_input = (
                    ui.textarea(
                        label="Shellcode (base64 please)",
                        placeholder="Enter shellcode here",
                        on_change=lambda e: validate_shellcode(e.value),
                    )
                    .classes("w-full")
                    .style(
                        "max-height: 400px; overflow-y: auto;"
                    )  # Set a max height and scrolling
                    .props("clearable")
                )
                shellcode_input.visible = False  # Set initial visibility to False

                # Queue compilation button
                ui.button("Queue for compilation", on_click=queue_compilation)

            # Right card (15% width) with rows for binary files
            with ui.card().classes("w-[25%] h-full flex flex-col"):
                ui.markdown("## Available Binaries")

                available_binaries = get_binaries()

                # Add rows with name and download button for each binary file
                for (
                    binary_name,
                    binary_path,
                ) in available_binaries.items():  # Iterate over key-value pairs
                    with ui.row().classes("justify-between items-center w-full"):
                        ui.label(binary_name)  # Display the binary name
                        ui.button(
                            "Download",
                            on_click=lambda path=binary_path: download_binary(
                                binary_name
                            ),
                        ).classes("ml-2")

    except Exception as e:
        logger.error(e)
        raise e


def validate_shellcode(b64_shellcode):
    if not is_base64(b64_shellcode):
        ui.notify("Shellcode is seemingly not base64!", type="warning")
