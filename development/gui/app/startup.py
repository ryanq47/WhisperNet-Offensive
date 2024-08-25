from nicegui import ui
from app.command_console import CommandConsole


## Want to move these somewhere else
@ui.page('/command/{client_id}')
def command_console(client_id: str):
    c = CommandConsole(client_id)
    # need to add a check in CommandConsole for if the client exists or not


def create_header():
    with ui.row().classes('q-pa-md').style('background-color: #f0f0f0; padding: 10px;'):
        ui.link('Home', '/').classes('q-mr-md')
        ui.link('Client 111', '/command/111-222-333-444').classes('q-mr-md')
        # Add more links as needed


#ui.link('111-222-333-444', '/command/111-222-333-444')
def hello() -> None:
    ui.notify('Hello World!')

def startup() -> None:
    @ui.page('/')
    def index():
        create_header()  # Add the header to the page
        ui.markdown("## HELLO THERE")
        ui.markdown("## PUT AN AGGRID TABLE THINGY HERE WITH CLIENT")

        ui.button('Click me', on_click=hello)