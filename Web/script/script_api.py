from nicegui import ui
import asyncio
from nicegui import ui
import socketio
from functools import partial

# from script.socket_client import sio_client, connect
import pathlib
import importlib.util
from config import Config


# a set of common web funcs to be inhereted
class WebCommon:
    """
    WebCommon: A set of functions for nicegui which are commonly used.

    This exists purely to be inhereted by classes in the CORE api structure

    Functions:

    - `notify(message: str): Calls nicegui ui.notify, puts a message on screen in top right`
    """

    def notify(self, message):
        """
        Creates a notification on screen
        """
        # note, CAN use self here, self from whoever inherets this
        ui.notify(message=message, position="top-right")


class Core:
    class Web:
        class Terminal(WebCommon):
            def __init__(
                self, agent_id, app, socket=None
            ):  # need to get socket in for unified websocket...
                """
                For interacting with the web gui terminal

                Functions:
                    - `broadcast(data:str)`:
                            Emit a message to all clients connected to the current room.
                        These messages will appear in the shell/terminal for the current client,
                        for any party that has the shell for this agent open.

                """
                self.agent_id = agent_id
                self.app = app  # Typically, this is NiceGUI's ui module
                self.label = None  # UI label to display messages
                # self.sio_client = connect()

            def print_to_terminal(self, data):
                """
                Prints output to the terminal (or console).
                """
                print(f"Terminal Output (Agent {self.agent_id}): {data}")

            def update_screen(self, text):
                """
                Updates or creates a label in the NiceGUI interface.
                """
                if self.label is None:
                    self.label = ui.label(text)
                else:
                    self.label.set_text(text)

            async def broadcast(self, message):
                """
                Broadcasts a message over the current websocket
                """

                # sio_client = socketio.AsyncClient()
                # await sio_client.connect("http://localhost:5000")  # local server
                # JOIN ROOM!
                await Config.socketio.emit(
                    # hardcoded for now
                    "join",
                    {"agent_id": self.agent_id},
                    namespace="/shell",
                )

                d = {"agent_id": self.agent_id, "data": message}
                await Config.socketio.emit(
                    event="display_on_terminal", data=d, namespace="/shell"
                )

    class Agent:  # agent stuff + calls/funcs for getting agent info
        def __init__(self):
            """ """
            ...

        def send():
            """
            Send command to agent


            returns command id
            """
            ...

            # web request

    class Websocket: ...  # webocket stuff + calls/funcs for websockets


# importing script
async def load_script(script_name, agent_id=None):
    print(f"Loading Script: {script_name}")
    # Build the script file path:
    path = pathlib.Path.cwd() / "data" / "scripts" / f"{script_name}.py"

    if not path.exists():
        print(f"Script file not found: {path}")
        return

    # Create a spec from the file location.
    spec = importlib.util.spec_from_file_location(script_name, str(path))
    if spec is None:
        print("Could not load spec for", str(path))
        return

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # remeber, using sio_client from sokcet_client

    # handler for each section
    # on_agent_connect
    on_agent_connect = getattr(module, "on_agent_connect", None)
    if on_agent_connect is None:
        print("Warning: 'on_agent_connect' attribute not found in module.")
    else:
        try:
            # setup socket handler, call .run when this connects
            Config.socketio.on("on_agent_connect", on_agent_connect.run)
            print("registered on_agent_connect to on_agent_connect.run")
        except Exception as e:
            print(f"Error running on_agent_connect.run(): {e}")

    # on_agent_first_connect
    on_agent_first_connect = getattr(module, "on_agent_first_connect", None)
    if on_agent_first_connect is None:
        print("Warning: 'on_agent_first_connect' attribute not found in module.")
    else:
        try:
            # setup socket handler, call .run when this connects
            Config.socketio.on(
                "on_agent_first_connect",
                on_agent_first_connect.run,
            )
            print("registered on_agent_first_connect to on_agent_first_connect.run")

        except Exception as e:
            print(f"Error running on_agent_first_connect.run(): {e}")

    # on_agent_data
    on_agent_data = getattr(module, "on_agent_data", None)
    if on_agent_data is None:
        print("Warning: 'on_agent_data' attribute not found in module.")
    else:
        try:
            # setup socket handler, call .run when this connects
            Config.socketio.on("on_agent_data", on_agent_data.run)
            print("registered on_agent_data to on_agent_data.run")

        except Exception as e:
            print(f"Error running on_agent_data.run(): {e}")

    # on_agent_data
    display_on_terminal = getattr(module, "display_on_terminal", None)
    if display_on_terminal is None:
        print("Warning: 'display_on_terminal' attribute not found in module.")
    else:
        try:
            # setup socket handler, call .run when this connects
            Config.socketio.on(
                "display_on_terminal", display_on_terminal.run, namespace="/shell"
            )
            print("registered display_on_terminal to display_on_terminal.run")

        except Exception as e:
            print(f"Error running display_on_terminal.run(): {e}")

    # send message to terminal that things are hooked up + script is loaded
    instance = Core.Web.Terminal(
        agent_id="45cb983e-9662-4410-b77f-5ed3ac2699cf", app=ui
    )
    await instance.broadcast(
        "1. Loaded script successfully & registered websocket stuff"
    )
