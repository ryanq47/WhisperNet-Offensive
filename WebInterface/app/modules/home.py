from nicegui import ui
from app.modules.ui_elements import create_header
from app.modules.config import Config
import logging
import requests

logger = logging.getLogger(__name__)

def homepage():
    try:
        create_header()  # Add the header to the page
        ui.markdown("# Whispernet-Offensive Client")

        # Get service data from the server
        service_data = get_service_data()

        # Extract active services from the data
        active_services = service_data.get("active_services", [])

        # Debugging: Print service data to console
        #print("GETTING SERVICES")
        #print(active_services)

        # Create a container for the grid layout
        with ui.row().classes('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full h-screen p-4'):
            for service in active_services:
                name = service.get("info", "Unknown Service")
                ip = service.get("ip", "N/A")
                port = service.get("port", "N/A")

                # Create a card for each active service
                logger.info("Temporarily making 10 of each card to fill it up")
                for i in range(1,10):
                    with ui.card().classes('w-full p-4'):# bg-gray-800 border border-gray-700 shadow-lg rounded-lg'):
                        # Card header
                        ui.markdown(f"### {name}").classes('text-white')
                        ui.markdown(f"#### Service Details").classes('text-white')

                        # Define table columns and rows like in the example
                        columns = [
                            {'name': 'label', 'label': 'Label', 'field': 'label', 'required': True, 'align': 'left'},
                            {'name': 'value', 'label': 'Value', 'field': 'value'},
                        ]
                        rows = [
                            {'label': 'Status', 'value': 'Active'},
                            {'label': 'IP Address', 'value': ip},
                            {'label': 'Port', 'value': port},
                        ]

                        # Use the correct row_key and table structure
                        ui.table(columns=columns, rows=rows, row_key='label').classes('w-full text-left text-sm text-white border')

                        # Add padding or margin if necessary
                        ui.markdown("<br>")

    except Exception as e:
        logger.error(e)
        raise e


def get_service_data() -> dict:
    """
    Function to retrieve client data from server.
    """
    try:
        url = Config().get_url() / "stats" /"services"
        token = Config().get_token()

        headers = {
            'Authorization': f'Bearer {token}'
        }

        logger.debug("Getting services from server")
        response = requests.get(url, headers=headers, verify=Config().get_verify_certs())

        if response.status_code == 200:
            data = response.json()
            client_data = data.get("data", {})
            logger.debug(f"Service data retrieved: {client_data}")  # Debugging: Log the client data
            return client_data
        else:
            logger.warning(f"Received a {response.status_code} status code when requesting {url}")
            return {}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e