from nicegui import ui
from app.modules.ui_elements import create_header
from app.modules.login import check_login
import requests
from app.modules.config import Config
import logging

logger = logging.getLogger(__name__)

@ui.page('/clients')
def clients():
    try:
        if not check_login():
            return

        create_header()  # Add the header to the page

        ui.markdown("# Clients")

        # Initial load of data into the grid
        #fetch_and_update_grid_data()
        # 
        raw_client_data = get_client_data()
        client_data = transform_client_data(raw_client_data)
        

        # Initialize the grid with empty data and unique row IDs based on client_id
        grid = ui.aggrid(
            {
                'columnDefs': [
                    {"headerName": "Client-ID", "field": "client_id", "sortable": True, "filter": "agTextColumnFilter", 'floatingFilter': True, 'checkboxSelection': True},
                    {"headerName": "Type", "field": "type", "sortable": True, "filter": "agTextColumnFilter", 'floatingFilter': True},
                    {"headerName": "Checkin", "field": "checkin", "sortable": True, "filter": "agTextColumnFilter", 'floatingFilter': True},
                    {"headerName": "CLI", "field": "url"},
                ],
                'rowData': client_data,  # Start with empty data
                'defaultColDef': {
                    'sortable': True,
                    'filter': True,
                    'resizable': True,
                    'flex': 1,
                },
                'pagination': True,
                'paginationPageSize': 10,
                'rowSelection': 'single',
                ':getRowId': '(params) => params.data.client_id',  # Use client_id as the unique row ID
            },
            html_columns=[3]  # Making only the 3rd column HTML rendered
        ).classes('max-h-80')  # Adjust height as needed

        def fetch_and_update_grid_data():
            """Fetches new data and updates specific cells without causing a full refresh."""
            try:
                raw_client_data = get_client_data()
                client_data = transform_client_data(raw_client_data)

                # Debugging: Print or log the fetched and transformed data
                #logger.debug(f"Fetched client data: {client_data}")

                # Update grid rows based on fetched client data
                for data in client_data:
                    client_id = data['client_id']
                    # Update cells using the run_row_method for specific clients
                    #update_client_data(client_id, 'checkin', data['checkin'])
                    #update_client_data(client_id, 'type', data['type'])
                    # You can update other fields similarly as needed
                    # run the setDataValue on the row
                    grid.run_row_method(client_id, 'setDataValue', 'checkin', data['checkin'])
                    print(f"updating {client_id} checkin")


            except Exception as e:
                logger.error(e)
                ui.notify("Failed to update client data")


        # Set a timer to update the grid data every second
        ui.timer(1.0, fetch_and_update_grid_data)

    except Exception as e:
        logger.error(e)
        ui.notify("An unknown error occurred - Check the logs")
        raise e

def get_client_data() -> dict:
    """
    Function to retrieve client data from server.
    """
    try:
        url = Config().get_url() / "clients"
        token = Config().get_token()

        headers = {
            'Authorization': f'Bearer {token}'
        }

        logger.debug("Getting clients from server")
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            client_data = data.get("data", {})
            logger.debug(f"Client data retrieved: {client_data}")  # Debugging: Log the client data
            return client_data
        else:
            logger.warning(f"Received a {response.status_code} status code when requesting {url}")
            return {}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e

def transform_client_data(raw_data):
    """Transforms raw client data dictionary into a list of dictionaries suitable for AG Grid."""
    transformed_data = []
    for key, client_info in raw_data.items():
        client_id = client_info["client_id"]
        url = f'/command/{client_id}'

        transformed_data.append({
            "checkin": client_info["checkin"],
            "client_id": client_id,
            "type": client_info["type"],
            "url": f'<button onclick="window.location.href=\'{url}\'">Open Shell</button>',
        })
    logger.debug(f"Transformed client data: {transformed_data}")  # Debugging: Log the transformed data
    return transformed_data
