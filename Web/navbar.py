"""
Navbar is in its own file for 2 reasons:
 1. De clutter main
 2. Allow it to be imported elsewhere, if/when routing is not done in main (ex, see error.py, it cannot have routing in main due to clutter + error handling)


"""

from settings import Settings
from nicegui import ui


# navbar is loaded everywhere so it's a good spot to do things that need to be done everywere
def navbar():
    Settings.apply_settings()

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

        ui.button(
            f"Settings",
            on_click=lambda agents: ui.navigate.to("/settings"),
            color="bg-neutral-600",
            icon="settings",
            # pin to bottom?
        ).classes("w-full text-slate-50").props("square flat condensed")
        ui.separator()

        # for i in range(0, 5):
        #     ui.button(f"Button {i}", on_click=..., color="bg-neutral-600").classes(
        #         "w-full text-slate-50"
        #     ).props("square flat condensed")
        #     ui.separator()

        # Toggle & set in user settings local storage
