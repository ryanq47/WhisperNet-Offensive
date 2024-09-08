from nicegui import ui
from app.modules.ui_elements import create_header
from app.modules.config import Config
from app.modules.login import check_login
import logging
import requests

logger = logging.getLogger(__name__)

@ui.page('/plugins')
def plugins():
    try:
        if not check_login():
            return

        create_header()  # Add the header to the page
        ui.markdown("# Server Plugins")

        # Get service data from the server
        service_data = get_service_data()

        # Extract active services from the data
        active_services = service_data.get("plugins", [])

        # Create a container for the stacked layout (one card per row)
        with ui.column().classes('w-full h-screen p-4 space-y-6'):
            for service in active_services:
                name = service.get("name", "Unknown Service")
                info = service.get("info", "No Description")
                start_url = service.get("start", "N/A")
                stop_url = service.get("stop", "N/A")

                # Create a collapsible card for each active service
                with ui.expansion(f"{name}").classes('w-full border'): #.props('dense')
                    # Row to contain header and buttons aligned on the right side
                    with ui.row().classes('w-full justify-between items-center'):
                        ui.markdown(f"### {name}").classes('text-white')  # Service name (header)
                        #ui.markdown(f"#### {info}").classes('text-white')  # Service name (header)

                        # Buttons aligned to the right of the header
                        with ui.row().classes('gap-2'):
                            ui.button('Start', on_click=lambda: start_ftp(start_url)).classes('bg-blue-500 text-white')
                            ui.button('Stop', on_click=lambda: stop_ftp(stop_url)).classes('bg-red-500 text-white')

                    ui.markdown(f"#### Plugin Details").classes('text-white')
                    ui.markdown(f"{info}").classes('text-white')

                    # Define table columns and rows
                    # sooooo unless this data is included in the dashboard, don't include?
                    # columns = [
                    #     {'name': 'label', 'label': 'Label', 'field': 'label', 'required': True, 'align': 'left'},
                    #     {'name': 'value', 'label': 'Value', 'field': 'value'},
                    # ]
                    # rows = [
                    #     {'label': 'Status', 'value': 'Active'},
                    #     {'label': 'IP Address', 'value': ip},
                    #     {'label': 'Port', 'value': port},
                    # ]

                    # # Table with service details
                    # ui.table(columns=columns, rows=rows, row_key='label').classes('w-full text-left text-sm text-white border')

                    # # Add padding or margin if necessary
                    # ui.markdown("<br>")
                    

    except Exception as e:
        logger.error(e)
        raise e

def start_ftp(start_url:str):
    try:
        url = Config().get_url() / start_url
        token = Config().get_token()

        headers = {
            'Authorization': f'Bearer {token}'
        }

        logger.debug("Getting services from server")
        response = requests.get(url, headers=headers, verify=Config().get_verify_certs())

        if response.status_code == 200:
            pass

        else:
            logger.warning(f"Received a {response.status_code} status code when requesting {url}")

        ui.notify(response.json().get("message","No message in response"))

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e

def stop_ftp(stop_url:str):
    try:
        url = Config().get_url() / stop_url
        token = Config().get_token()

        headers = {
            'Authorization': f'Bearer {token}'
        }

        logger.debug("Getting services from server")
        response = requests.get(url, headers=headers, verify=Config().get_verify_certs())

        if response.status_code == 200:
            pass

        else:
            logger.warning(f"Received a {response.status_code} status code when requesting {url}")

        ui.notify(response.json().get("message","No message in response"))

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e



def get_service_data() -> dict:
    """
    Function to retrieve client data from server.
    """
    try:
        url = Config().get_url() / "stats" / "plugins"
        token = Config().get_token()

        headers = {
            'Authorization': f'Bearer {token}'
        }

        logger.debug("Getting services from server")
        response = requests.get(url, headers=headers, verify=Config().get_verify_certs())

        if response.status_code == 200:
            data = response.json()
            #print(data)
            client_data = data.get("data", {})
            logger.debug(f"Service data retrieved: {client_data}")  # Debugging: Log the client data
            return client_data
        else:
            logger.warning(f"Received a {response.status_code} status code when requesting {url}")
            return {}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e
