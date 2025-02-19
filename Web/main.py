from nicegui import events, ui, app
from searchbar import Search
from agent import AgentView, AgentsPage
from listener import ListenerView, ListenersPage
from about import AboutView
from home import HomeView
from config import Config, ThemeConfig
from settings import Settings
from error import ErrorPage
from navbar import navbar
from logs import LogsView
from auth import AuthView, check_login
from credstore import CredentialStore
from files import FilePage
import argparse


parser = argparse.ArgumentParser(description="Set the API host for the application.")

# Add the API host argument
parser.add_argument(
    "--api-host",
    type=str,
    required=True,
    help="The API host URL (e.g., http://localhost:8080).",
)

# Parse the arguments
args = parser.parse_args()

# Access the API host value
api_host = args.api_host
print(f"API Host set to: {api_host}")

# yarl this
Config.API_HOST = api_host  # "http://192.168.23.128:8081/"


# @ui.page("/animation")
# def animation_page():
#     # Initial position of the walking element
#     position = {"left": 0}

#     # Function to update position
#     def move():
#         position["left"] += 10  # Move 10 pixels to the right
#         if position["left"] > 500:  # Reset position after reaching the end
#             position["left"] = 0
#         walking_element.style(f"position: absolute; left: {position['left']}px;")

#     # Create the walking element
#     with ui.row().style("position: relative; height: 100px;"):
#         walking_element = ui.label("========>").style("position: absolute; left: 0px;")

#     # Timer to trigger the move function
#     ui.timer(interval=0.1, callback=move)  # Update position every 100ms


@ui.page("/")
def index():
    check_login()
    navbar()
    # little hack to set hieght to full here. Makes it so it is the full page, and not have a scrollbar
    # with ui.element().classes():
    # Fixed by doing a.class("absolute-center")
    # Need to have this pop search cuz aboslute cetner cetners EVERYTHING
    h = HomeView()
    h.render()


@ui.page("/settings")
def settings():
    check_login()
    main_container = navbar()
    with main_container:
        s = Settings()
        s.render()


@ui.page("/credstore")
def settings():
    check_login()
    main_container = navbar()
    with main_container:
        c = CredentialStore()
        c.render()


@ui.page("/search")
def search():
    check_login()
    main_container = navbar()
    with main_container:
        s = Search()
        s.spawn_search_bar()


@ui.page("/about")
def about():
    check_login()
    main_container = navbar()
    with main_container:
        a = AboutView()
        a.render()


@ui.page("/agent/{uuid}")
def agent_view_page(uuid: str):
    check_login()
    main_container = navbar()
    with main_container:
        a = AgentView(agent_id=uuid)
        a.render()


@ui.page("/agents")
def agent_view_page():
    check_login()
    main_container = navbar()
    with main_container:
        # needs to be renamed, prolly re-factored too
        a = AgentsPage()
        a.render()


@ui.page("/listener/{uuid}")
def listener_view_page(uuid: str):
    check_login()
    main_container = navbar()
    with main_container:
        a = ListenerView(listener_id=uuid)
        a.render()


@ui.page("/listeners")
def agent_view_page():
    check_login()
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
def agent_view_page():
    check_login()
    main_container = navbar()
    with main_container:
        a = FilePage()
        a.render()


@ui.page("/auth")
def auth_view_page():
    # navbar()
    a = AuthView()
    a.render()


# Note - this dir has no auth
app.add_static_files(
    "/static", "static"
)  # Serve files from the 'static' directory, to /static
ui.run(storage_secret="URMOM", host="0.0.0.0", favicon="/static/icon_full.ico")
