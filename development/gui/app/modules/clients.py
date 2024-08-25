from nicegui import ui

## Todo:

# - [  ] make this stretch the whole screen
# - [ ] get real data/make request
# - [  ] style match

# Define some fake data for the AG Grid
fake_data = [
    {"name": "Alice", "age": 25, "country": "USA"},
    {"name": "Bob", "age": 30, "country": "Canada"},
    {"name": "Charlie", "age": 35, "country": "UK"},
    {"name": "David", "age": 40, "country": "Australia"},
    {"name": "Eva", "age": 45, "country": "Germany"},
]

# Create the NiceGUI page
@ui.page('/clients')
def clients():
    ui.markdown("## AG Grid with Fake Data")

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
        }
    )
