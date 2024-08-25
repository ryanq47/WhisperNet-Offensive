from nicegui import ui

# Creates a navbar
def create_header():
    with ui.header() as header:
        ui.label('WhisperNet-Offensive').classes('text-h6')
        ui.button('Home', on_click=lambda: ui.open('/home'))
        ui.button('Clients', on_click=lambda: ui.open('/clients'))#.props('flat')
        ui.button('??', on_click=lambda: ui.open('/contact'))#.props('flat')
