from nicegui import ui
# need to import things up here (or do a plugin loader) to make sure routes are loaded
from app.modules.command_console import CommandConsole
from app.modules.home import homepage
from app.modules.clients import clients

def startup() -> None:
    @ui.page('/')
    def index():
        homepage()

    @ui.page('/home')
    def home():
        homepage()
        # make this do the same as /

## Want to move these somewhere else? if possible
@ui.page('/command/{client_id}')
def command_console(client_id: str):
    c = CommandConsole(client_id)
    # need to add a check in CommandConsole for if the client exists or not

