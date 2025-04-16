from nicegui import events, ui, app
from agent import AgentView, AgentsPage, OldReliable
from listener import ListenerView, ListenersPage
from about import AboutView
from home import HomeView
from config import Config, ThemeConfig
from settings import Settings
from error import ErrorPage
from navbar import navbar
from logs import LogsView
from auth import AuthView, check_login
from credstore import CredentialStore, CredentialStorePage
from multi_console import MultiConsolePage
from files import FilePage
import argparse
import logging
import socketio
import asyncio

logging.getLogger("niceGUI").setLevel(logging.CRITICAL)


# Command-line parsing (unchanged)
parser = argparse.ArgumentParser(description="Set the API host for the application.")
parser.add_argument(
    "--api-host",
    type=str,
    required=True,
    help="The API host URL (e.g., http://localhost:8080).",
)
args = parser.parse_args()
api_host = args.api_host
print(f"API Host set to: {api_host}")
# Set the config accordingly (example)
Config.API_HOST = api_host


# ----------------
# Socket stuff
# ----------------

sio = socketio.AsyncClient()
Config.socketio = sio


async def connect_to_client_socket():
    # Connect to the sio server and join the /shell namespace.
    await sio.connect("http://127.0.0.1:8081", namespaces=["/shell"])
    # Instead of blocking forever, run sio.wait() as a background task.
    # asyncio.create_task(sio.wait())


async def disconnect_from_client_socket():
    if sio.connected:
        await sio.disconnect()
        print("sio connection closed.")


@ui.page("/")
async def index():
    check_login()
    if not sio.connected:
        await connect_to_client_socket()
    navbar()
    # little hack to set hieght to full here. Makes it so it is the full page, and not have a scrollbar
    # with ui.element().classes():
    # Fixed by doing a.class("absolute-center")
    # Need to have this pop search cuz aboslute cetner cetners EVERYTHING
    h = HomeView()
    h.render()


@ui.page("/settings")
async def settings():
    check_login()
    if not sio.connected:
        await connect_to_client_socket()
    main_container = navbar()
    with main_container:
        s = Settings()
        s.render()


@ui.page("/credstore")
async def settings():
    check_login()
    if not sio.connected:
        await connect_to_client_socket()
    main_container = navbar()
    with main_container:
        c = CredentialStorePage()
        c.render()


@ui.page("/multi-console")
async def settings():
    check_login()
    if not sio.connected:
        await connect_to_client_socket()
    main_container = navbar()
    with main_container:
        mc = MultiConsolePage()
        mc.render()


@ui.page("/about")
async def about():
    check_login()
    if not sio.connected:
        await connect_to_client_socket()
    main_container = navbar()
    with main_container:
        a = AboutView()
        a.render()


@ui.page("/agent/{uuid}")
async def agent_view_page(uuid: str):
    check_login()
    if not sio.connected:
        await connect_to_client_socket()
    main_container = navbar()
    with main_container:
        a = AgentView(agent_id=uuid)
        await a.render()


@ui.page("/agents")
async def agent_view_page():
    check_login()
    if not sio.connected:
        await connect_to_client_socket()
    main_container = navbar()
    with main_container:
        # needs to be renamed, prolly re-factored too
        a = AgentsPage()
        a.render()


@ui.page("/old-reliable")
async def old_reliable():
    check_login()
    if not sio.connected:
        await connect_to_client_socket()
    main_container = navbar()
    with main_container:
        s = OldReliable()
        await s.render()


@ui.page("/listener/{uuid}")
async def listener_view_page(uuid: str):
    check_login()
    if not sio.connected:
        await connect_to_client_socket()
    main_container = navbar()
    with main_container:
        a = ListenerView(listener_id=uuid)
        a.render()


@ui.page("/listeners")
async def agent_view_page():
    check_login()
    if not sio.connected:
        await connect_to_client_socket()
    main_container = navbar()
    with main_container:
        a = ListenersPage()
        a.render()


# @ui.page("/logs")
# def agent_view_page():
#     check_login()
#     main_container = navbar()
#     with main_container:
#         a = LogsView()
#         a.render()


@ui.page("/files")
async def agent_view_page():
    check_login()
    if not sio.connected:
        await connect_to_client_socket()
    main_container = navbar()
    with main_container:
        a = FilePage()
        a.render()


@ui.page("/auth")
async def auth_view_page():
    if not sio.connected:
        await connect_to_client_socket()
    # navbar()
    a = AuthView()
    a.render()


# Note - this dir has no auth
app.add_static_files(
    "/static", "static"
)  # Serve files from the 'static' directory, to /static
ui.run(storage_secret="URMOM", host="0.0.0.0")
