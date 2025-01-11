from nicegui import events, ui, app
from searchbar import Search
from agent import AgentView, AgentsView
from listener import ListenerView, ListenersView
from about import AboutView
from home import HomeView
from config import Config, ThemeConfig

# yarl this
Config.API_HOST = "http://192.168.23.128:8081/"


def navbar():
    with ui.header().classes(
        "items-center justify-between bg-neutral-800 h-20 px-4 h-1/6"
    ):
        ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props(
            "flat color=white"
        )

        # Large screen buttons (hidden on small screens)
        with ui.row().classes():
            with ui.button_group().props("outline"):
                ui.button(
                    "Home", icon="home", on_click=lambda: ui.navigate.to("/")
                ).props("flat color=white").classes(
                    "text-xs py-2"
                )  # Smaller height
                # ui.button("??", icon="map").props("flat color=white").classes(
                #     "py-2 text-xs"
                # )  # Smaller height
                ui.button(
                    "Search",
                    icon="search",
                    on_click=lambda: ui.navigate.to("/search"),
                ).props("flat color=white").classes("py-2 text-xs")
                ui.button(
                    "About", icon="help", on_click=lambda: ui.navigate.to("/about")
                ).props("flat color=white").classes("py-2 text-xs")

        # Small screen buttons (hidden on large screens)
        with ui.row().classes("sm:hidden items-center space-x-4 h-full"):
            ui.button(icon="shopping_cart").props("flat color=white").classes(
                "py-2 text-xs"
            )
            ui.button(icon="feed").props("flat color=white").classes("py-2 text-xs")
            ui.button(icon="perm_phone_msg").props("flat color=white").classes(
                "py-2 text-xs"
            )

        # placeholder to keep items in cetner. disabled
        # maybe put something else here?
        # Menu button (typically for mobile)
        ui.button(icon="menu").props("flat color=white").classes(
            "h-full text-xs py-2"
        ).disable()  # Added text size and padding

    with ui.left_drawer(value=False).classes("bg-neutral-600") as left_drawer:
        ui.button(
            f"Home",
            on_click=lambda agents: ui.navigate.to("/"),
            icon="home",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")
        ui.separator()

        ui.button(
            f"Search",
            on_click=lambda agents: ui.navigate.to("/search"),
            color="bg-neutral-600",
            icon="search",
        ).classes("w-full text-slate-50").props("square flat condensed")
        ui.separator()

        ui.button(
            f"Agents",
            on_click=lambda agents: ui.navigate.to("/agents"),
            color="bg-neutral-600",
            icon="computer",
        ).classes("w-full text-slate-50").props("square flat condensed")
        ui.separator()

        ui.button(
            f"Listeners",
            on_click=lambda listeners: ui.navigate.to("/listeners"),
            color="bg-neutral-600",
            icon="headphones",
        ).classes("w-full text-slate-50").props("square flat condensed")
        ui.separator()

        ui.button(
            f"About",
            on_click=lambda agents: ui.navigate.to("/about"),
            color="bg-neutral-600",
            icon="help",
        ).classes("w-full text-slate-50").props("square flat condensed")
        ui.separator()

        # for i in range(0, 5):
        #     ui.button(f"Button {i}", on_click=..., color="bg-neutral-600").classes(
        #         "w-full text-slate-50"
        #     ).props("square flat condensed")
        #     ui.separator()


@ui.page("/")
def index():
    navbar()
    # little hack to set hieght to full here. Makes it so it is the full page, and not have a scrollbar
    # with ui.element().classes():
    # Fixed by doing a.class("absolute-center")
    # Need to have this pop search cuz aboslute cetner cetners EVERYTHING
    h = HomeView()
    h.render()


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
