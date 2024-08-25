from nicegui import ui
from app.modules.ui_elements import create_header

def homepage():
    create_header()  # Add the header to the page
    ui.markdown("## HELLO THERE")
    ui.markdown("## PUT AN AGGRID TABLE THINGY HERE WITH CLIENT")

    #ui.button('Click me', on_click=hello)