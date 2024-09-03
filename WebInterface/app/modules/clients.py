from nicegui import ui
from app.modules.ui_elements import create_header
from app.modules.login import check_login
import requests
from app.modules.config import Config
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

@ui.page('/clients')
def clients():
    try:
        if not check_login():
            return


        ui.markdown("# Clients")
        
        raw_client_data = get_client_data()
        client_data = transform_client_data(raw_client_data)

        # problem: Vh 100 is bigger than the page, prolly cause margin, but disabling margin doenst work
        create_header()  # Add the header to the page

        with ui.column().classes('h-auto w-full'): # add border to show border

            # The grid container itself with defined height and full width
            grid = ui.aggrid(
                {
                    'columnDefs': [
                        {"headerName": "Client-ID", "field": "client_id", "sortable": True, "filter": "agTextColumnFilter", 'floatingFilter': True, 'checkboxSelection': True},
                        {"headerName": "Type", "field": "type", "sortable": True, "filter": "agTextColumnFilter", 'floatingFilter': True},
                        {"headerName": "Checkin (UTC)", "field": "checkin", "sortable": True, "filter": "agTextColumnFilter", 'floatingFilter': True},
                        {"headerName": "CLI", "field": "url"},
                    ],
                    'rowData': client_data,  # Use your actual client data here
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
                    #'autoHeight':True
                    
                },
                html_columns=[3],  # Making only the 3rd column HTML rendered
                #theme="quartz-dark"
            )
            
            #grid.classes('w-full max-w-full') # Adjust the grid classes for full height and width
            # LEAVE! allows it to grow. 
            grid.classes('flex-grow') #w-full h-full')#.style('width: 100%; height: 95vh')
            ui.chat_message("This AgGrid is being frustrating... and does not want to scale properly, or have colored themes apply to it")

            #ui.space()
        def fetch_and_update_grid_data():
            """Fetches new data and updates specific cells without causing a full refresh."""
            try:
                raw_client_data = get_client_data()
                client_data = transform_client_data(raw_client_data)

                # Update checkin time
                for data in client_data:
                    utc_checkin = datetime.fromtimestamp(int(data['checkin']), timezone.utc)
                    formatted_checkin = utc_checkin.astimezone().strftime('%Y-%m-%d %H:%M:%S')

                    client_id = data['client_id']
                    grid.run_row_method(client_id, 'setDataValue', 'checkin', formatted_checkin)

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
        response = requests.get(url, headers=headers, verify=Config().get_verify_certs())

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
