from nicegui import ui
from app.modules.ui_elements import create_header
from app.modules.login import check_login
import requests
from app.modules.config import Config
import logging

logger = logging.getLogger(__name__)

## Todo:

# - [x] make this stretch the whole screen
# - [x] get real data/make request
# - [x] style match

# Define some fake data for the AG Grid
fake_data = [
    {"name": "Alice", "age": 25, "country": "USA"},
    {"name": "Bob", "age": 30, "country": "Canada"},
    {"name": "Charlie", "age": 35, "country": "UK"},
    {"name": "David", "age": 40, "country": "Australia"},
    {"name": "Eva", "age": 45, "country": "<a href='https://facebook.com'>https://facebook.com</a>"},
]

# Create the NiceGUI page
@ui.page('/clients')
def clients():
    if not check_login():
        return

    create_header()  # Add the header to the page

    ui.markdown("## AG Grid with Fake Data")

    client_data = get_client_data()

    # Enhanced AG Grid setup
    ui.aggrid(
        {
            'columnDefs': [
                {"headerName": "Name", "field": "name", "sortable": True, "filter": "agTextColumnFilter"},
                {"headerName": "Age", "field": "age", "sortable": True, "filter": "agNumberColumnFilter", "type": "numericColumn"},
                {"headerName": "Country", "field": "country", "sortable": True, "filter": "agTextColumnFilter"},
            ],
            'rowData': fake_data,
            'defaultColDef': {  # Default settings for all columns
                'sortable': True,  # Enable sorting for all columns
                'filter': True,    # Enable filtering for all columns
                'resizable': True, # Allow column resizing
            },
            'pagination': True,        # Enable pagination
            'paginationPageSize': 10,  # Set the number of rows per page
            'rowSelection': 'single',  # Enable single row selection
        }, html_columns=[2] # making only 2nd row html rendered
    )


def get_client_data() -> dict:
    """
    Function to retrieve client data from server
    """
    try:
        url = Config().get_url() / "clients"
        token = Config().get_token()

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # Send a synchronous GET request
        response = requests.get(url, headers=headers)  # Ensure headers are included in the request

        if response.status_code == 200:
            data = response.json()

            # Retrieve client data from JSON response
            client_data = data.get("data", {})
            #print(client_data)
            return client_data
        else:
            logger.warning(f"Received a {response.status_code} status code when requesting {url}")
            #logger.debug(response.text)
            return {}  # Handle failed response here by returning an empty dictionary

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e
