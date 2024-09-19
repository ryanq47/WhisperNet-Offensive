from nicegui import ui, app
# need to import things up here (or do a plugin loader) to make sure routes are loaded
from app.modules.command_console import CommandConsole
from app.modules.home import homepage
from app.modules.clients import clients
from app.modules.login import check_login
import app.modules.login
import app.modules.static
import app.modules.plugins


def startup() -> None:
    @ui.page('/')
    def index():
        if not check_login():
            return

        homepage()

    @ui.page('/home')
    def home():
        if not check_login():
            return

        homepage()
        # make this do the same as /

## Want to move these somewhere else? if possible
@ui.page('/command/{client_id}')
def command_console(client_id: str):
    if not check_login():
        return

    c = CommandConsole(client_id)
    # need to add a check in CommandConsole for if the client exists or not

