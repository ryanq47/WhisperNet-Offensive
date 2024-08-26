from nicegui import ui
from app.modules.ui_elements import create_header

def homepage():
    create_header()  # Add the header to the page
    ui.markdown("Whispernet-Offensive Client")

    #ui.button('Click me', on_click=hello)