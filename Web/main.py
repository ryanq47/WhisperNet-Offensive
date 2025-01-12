from nicegui import events, ui, app
from searchbar import Search
from agent import AgentView, AgentsView
from listener import ListenerView, ListenersView
from about import AboutView
from home import HomeView
from config import Config, ThemeConfig
from settings import Settings
from error import ErrorPage
from navbar import navbar

# yarl this
Config.API_HOST = "http://192.168.23.128:8081/"


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
    navbar()

    # little hack to set hieght to full here. Makes it so it is the full page, and not have a scrollbar
    # with ui.element().classes():
    # Fixed by doing a.class("absolute-center")
    # Need to have this pop search cuz aboslute cetner cetners EVERYTHING
    h = HomeView()
    h.render()


@ui.page("/settings")
def settings():
    navbar()
    s = Settings()
    s.render()


@ui.page("/search")
def search():
    navbar()
    s = Search()
    s.spawn_search_bar()


@ui.page("/about")
def about():
    navbar()
    a = AboutView()
    a.render()


@ui.page("/agent/{uuid}")
def agent_view_page(uuid: str):
    navbar()
    a = AgentView(agent_id=uuid)
    a.render()


@ui.page("/agents")
def agent_view_page():
    navbar()
    a = AgentsView()
    a.render()


@ui.page("/listener/{uuid}")
def listener_view_page(uuid: str):
    navbar()
    a = ListenerView(listener_id=uuid)
    a.render()


@ui.page("/listeners")
def agent_view_page():
    navbar()
    a = ListenersView()
    a.render()


app.add_static_files(
    "/static", "static"
)  # Serve files from the 'static' directory, to /static
ui.run(storage_secret="URMOM", host="0.0.0.0")