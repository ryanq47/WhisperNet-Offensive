from script.script_api import Core
from nicegui import ui

# --------------------
# Example Script contents
# --------------------
"""
Idea here:

Dedicated classes that do different things


Socket: "on_agent_connect"
Room: /<agent_id>
Desc: Triggered when agent connects

Socket: "on_agent_first_connect"
Room: /<agent_id>
Desc: Triggered when agent *first* checks in

Socket: "on_agent_data"
Room: /<agent_id>
Desc: Triggered when agent gives data (NOT checkin)

"""

# sio = socketio.Client()
# sio.connect("http://localhost:5000")
interface = Core.Web.Terminal(agent_id="45cb983e-9662-4410-b77f-5ed3ac2699cf", app=ui)


class on_agent_connect:
    async def run(data):
        # interface.broadcast("Agent connected")
        await interface.broadcast("on_agent_connect")
        print("SCRIPT: on_agent_connect")
        # await interface.broadcast("on_agent_connect")
        # replace this with interface.broadcast, this is just a dev call
        # sio.emit("on_connect", {"info": "Client connected"})
        # interface.notify("on_agent_connect")


class on_agent_first_connect:
    async def run(data):
        # Instantiate our Core.Web.Interface with NiceGUI's ui as our 'app'
        await interface.broadcast("on_agent_first_connect")
        print("SCRIPT: on_agent_first_connect")
        # interface.notify("on_agent_first_connect")


class on_agent_data:
    async def run(data):
        await interface.broadcast("on_agent_data")
        print("SCRIPT: on_agent_data")
        # interface.notify("on_agent_data")


class display_on_terminal:
    """
    Modify the display on terminal websocket, to do things

    Might not need here later, this is meant to be more of an internal/non accessible one, emitted from the core api
    """

    async def run(data):
        # Instantiate our Core.Web.Interface with NiceGUI's ui as our 'app'
        # interface.broadcast("Some data printed to terminal.")
        # interface.broadcast("SomeData")
        await interface.broadcast("Script says hello from interface.broadcast")
        print("SCRIPT: display_on_terminal")
        # interface.notify("display_on_terminal")
