"""
Navbar is in its own file for 2 reasons:
 1. De clutter main
 2. Allow it to be imported elsewhere, if/when routing is not done in main (ex, see error.py, it cannot have routing in main due to clutter + error handling)


"""

from settings import Settings, LocalSettings
from nicegui import ui, app


# navbar is loaded everywhere so it's a good spot to do things that need to be done everywere
def navbar():
    # Apply per-user settings.
    LocalSettings.apply_settings()
    current_settings = app.storage.user.get("settings", {})
    # # ui.label("WOW THIS WORKS SO MUCH BETTER WITH NO NAVBAR")
    if current_settings.get("More Fun Mode", False):
        fun_navbar()  # creates a top-level header
    else:
        normal_navbar()  # creates a top-level header

    # Create the main container that all page content will use.
    # Adjust the subtraction values to match your header (and sidebar, if any) heights.
    main_container = (
        ui.element()
        .classes("")  # overflow-auto for scroll if it goes long
        .style(
            "border-color: red; height: calc(100vh - 150px); width: calc(100vw - 25px);"
        )
    )
    return main_container


def fun_navbar():
    current_settings = app.storage.user.get("settings", {})

    # Option 1: Just change the background image via .style(...)
    # We'll use a popular Nyan Cat GIF from giphy (or your own URL).
    # You can also do background-size: cover; or whichever suits your design.
    # A fixed height for your header (h-20 = 5rem).
    # Also note the color=white in props for buttons and text classes to ensure visibility.
    with ui.header(elevated=True, wrap=True).classes(
        "flex items-center justify-between h-20 px-4"
    ).style(
        """
        /* Example gradient from purple-500 to teal-400 */
        background: linear-gradient(to right,rgb(45, 45, 46),rgb(179, 179, 179));
        color: white;
        """
    ):
        ui.button(
            icon="menu",
            on_click=lambda: left_drawer.toggle(),
        ).props("flat color=white")

        # If you remove "hidden sm:flex" and "sm:hidden", you won't hide them on any screen size.
        with ui.row().classes("items-center space-x-4"):  # Always visible row
            with ui.button_group().props("outline"):
                ui.button(
                    "Home", icon="home", on_click=lambda: ui.navigate.to("/")
                ).props("flat color=white").classes("text-xs py-2")

                ui.button(
                    "Search",
                    icon="search",
                    on_click=lambda: ui.navigate.to("/search"),
                ).props("flat color=white").classes("py-2 text-xs")

                ui.button(
                    "About", icon="help", on_click=lambda: ui.navigate.to("/about")
                ).props("flat color=white").classes("py-2 text-xs")

        # An extra button on the far right as an example
        ui.button(icon="menu").props("flat color=white").classes(
            "py-2 text-xs"
        ).disable()

    # drawer stuff
    with ui.left_drawer(value=False).classes("bg-neutral-600") as left_drawer:
        # Dashboard Section
        ui.label("Dashboard").classes("text-slate-200 text-lg font-bold px-4 py-2")
        ui.button(
            "Home",
            on_click=lambda: ui.navigate.to("/"),
            icon="home",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")
        ui.button(
            "Search",
            on_click=lambda: ui.navigate.to("/search"),
            icon="search",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")
        ui.separator().classes("my-2 border-slate-400")

        # Operations Section
        ui.label("Operations").classes("text-slate-200 text-lg font-bold px-4 py-2")

        ui.button(
            "Agents",
            on_click=lambda: ui.navigate.to("/agents"),
            icon="computer",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")
        ui.button(
            "Listeners",
            on_click=lambda: ui.navigate.to("/listeners"),
            icon="headphones",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")
        ui.button(
            "Hosted Files",
            on_click=lambda: ui.navigate.to("/files"),
            icon="dns",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")

        # Info Section
        ui.separator().classes("my-2 border-slate-400")
        ui.label("Misc").classes("text-slate-200 text-lg font-bold px-4 py-2")
        # ui.button(
        #     "Logs",
        #     on_click=lambda: ui.navigate.to("/logs"),
        #     icon="article",
        #     color="bg-neutral-600",
        # ).classes("w-full text-slate-50").props("square flat condensed")

        ui.button(
            "Settings",
            on_click=lambda: ui.navigate.to("/settings"),
            icon="settings",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")
        # ui.separator().classes("my-2 border-slate-400")
        ui.button(
            "About",
            on_click=lambda: ui.navigate.to("/about"),
            icon="help",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")

        # Account Section
        # ui.label("👤 Account").classes("text-slate-200 text-lg font-bold px-4 py-2")
        ui.button(
            "Logout",
            on_click=lambda: ui.navigate.to("/logout"),
            icon="logout",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")


def normal_navbar():
    current_settings = app.storage.user.get("settings", {})

    # Option 1: Just change the background image via .style(...)
    # We'll use a popular Nyan Cat GIF from giphy (or your own URL).
    # You can also do background-size: cover; or whichever suits your design.
    # A fixed height for your header (h-20 = 5rem).
    # Also note the color=white in props for buttons and text classes to ensure visibility.
    with ui.header(elevated=True, wrap=True).classes(
        "flex items-center justify-between h-20 px-4"
    ).style(
        """
        /* Example gradient from purple-500 to teal-400 */
        background: linear-gradient(to right,rgb(45, 45, 46),rgb(179, 179, 179));
        color: white;
        """
    ):
        ui.button(
            icon="menu",
            on_click=lambda: left_drawer.toggle(),
        ).props("flat color=white")

        # If you remove "hidden sm:flex" and "sm:hidden", you won't hide them on any screen size.
        with ui.row().classes("items-center space-x-4"):  # Always visible row
            with ui.button_group().props("outline"):
                ui.button(
                    "Home", icon="home", on_click=lambda: ui.navigate.to("/")
                ).props("flat color=white").classes("text-xs py-2")

                ui.button(
                    "Search",
                    icon="search",
                    on_click=lambda: ui.navigate.to("/search"),
                ).props("flat color=white").classes("py-2 text-xs")

                ui.button(
                    "About", icon="help", on_click=lambda: ui.navigate.to("/about")
                ).props("flat color=white").classes("py-2 text-xs")

        # An extra button on the far right as an example
        ui.button(icon="menu").props("flat color=white").classes(
            "py-2 text-xs"
        ).disable()

    # drawer stuff
    with ui.left_drawer(value=False).classes("bg-neutral-600") as left_drawer:
        # Dashboard Section
        ui.label("Dashboard").classes("text-slate-200 text-lg font-bold px-4 py-2")
        ui.button(
            "Home",
            on_click=lambda: ui.navigate.to("/"),
            icon="home",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")
        ui.button(
            "Search",
            on_click=lambda: ui.navigate.to("/search"),
            icon="search",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")
        ui.separator().classes("my-2 border-slate-400")

        # Operations Section
        ui.label("Operations").classes("text-slate-200 text-lg font-bold px-4 py-2")

        ui.button(
            "Agents",
            on_click=lambda: ui.navigate.to("/agents"),
            icon="computer",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")
        ui.button(
            "Listeners",
            on_click=lambda: ui.navigate.to("/listeners"),
            icon="headphones",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")
        ui.button(
            "Hosted Files",
            on_click=lambda: ui.navigate.to("/files"),
            icon="dns",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")

        # Info Section
        ui.separator().classes("my-2 border-slate-400")
        ui.label("Misc").classes("text-slate-200 text-lg font-bold px-4 py-2")
        # ui.button(
        #     "Logs",
        #     on_click=lambda: ui.navigate.to("/logs"),
        #     icon="article",
        #     color="bg-neutral-600",
        # ).classes("w-full text-slate-50").props("square flat condensed")

        ui.button(
            "Settings",
            on_click=lambda: ui.navigate.to("/settings"),
            icon="settings",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")
        # ui.separator().classes("my-2 border-slate-400")
        ui.button(
            "About",
            on_click=lambda: ui.navigate.to("/about"),
            icon="help",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")

        # Account Section
        # ui.label("👤 Account").classes("text-slate-200 text-lg font-bold px-4 py-2")
        ui.button(
            "Logout",
            on_click=lambda: ui.navigate.to("/logout"),
            icon="logout",
            color="bg-neutral-600",
        ).classes("w-full text-slate-50").props("square flat condensed")
