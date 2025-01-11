from nicegui import ui
from app.modules.ui_elements import create_header
from app.modules.config import ThemeConfig
import logging
import requests

logger = logging.getLogger(__name__)


def homepage():
    try:
        create_header()  # Add the header to the page
        ui.markdown("# Whispernet-Offensive Client")

        # Container to hold the service grid, which will be updated
        grid_container = ui.row().classes(
            "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full h-screen p-4"
        )

        # Function to refresh the service data and update the UI
        def refresh_services():
            service_data = get_service_data()
            active_services = service_data.get("active_services", [])

            grid_container.clear()  # Clear previous cards
            for service in active_services:
                name = service.get("name", "Unknown Service")
                info = service.get("info", "No info")
                ip = service.get("ip", "N/A")
                port = service.get("port", "N/A")

                # Create a card for each active service
                with grid_container:  # Add cards dynamically
                    with ui.card().classes("w-full p-4"):
                        # Card header
                        ui.markdown(f"### {name}").classes("text-white")
                        ui.markdown(f"#### Service Details").classes("text-white")
                        ui.markdown(f"{info}").classes("text-white")

                        # Define table columns and rows
                        columns = [
                            {
                                "name": "label",
                                "label": "Label",
                                "field": "label",
                                "required": True,
                                "align": "left",
                            },
                            {"name": "value", "label": "Value", "field": "value"},
                        ]
                        rows = [
                            {"label": "Status", "value": "Active"},
                            {"label": "IP Address", "value": ip},
                            {"label": "Port", "value": port},
                        ]

                        # Display table
                        ui.table(columns=columns, rows=rows, row_key="label").classes(
                            "w-full text-left text-sm text-white border"
                        )

                        ui.markdown("<br>")  # Add padding or margin if necessary

        # Set a timer to refresh the services every X seconds (e.g., 10 seconds)
        ui.timer(10, refresh_services)  # Refresh every 10 seconds
        refresh_services()  # Initial load of the data

    except Exception as e:
        logger.error(e)
        raise e


def get_service_data() -> dict:
    """
    Function to retrieve client data from server.
    """
    try:
        url = ThemeConfig().get_url() / "stats" / "services"
        token = ThemeConfig().get_token()

        headers = {"Authorization": f"Bearer {token}"}

        logger.debug("Getting services from server")
        response = requests.get(
            url, headers=headers, verify=ThemeConfig().get_verify_certs()
        )

        if response.status_code == 200:
            data = response.json()
            client_data = data.get("data", {})
            logger.debug(f"Service data retrieved: {client_data}")
            return client_data
        else:
            logger.warning(
                f"Received a {response.status_code} status code when requesting {url}"
            )
            return {}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e
