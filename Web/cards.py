from nicegui import ui
from config import Config


def agent_card(data: dict):
    """Cards suited for Agent cards.

    Args:
        data (dict): dict containing agent data from server
    """
    # check to make sure the data key is in the dict, if not, send to unknown_card
    data_key = data.get("data", None)
    if not data_key:
        unknown_card(data)

    # then on success/if data_key, rename back to data for compatibility with already built logic
    data = data_key

    # data = data["data"]
    # Full-width card
    with ui.card().classes("w-full bg-gray-100 shadow-md p-4"):
        # Create a row with left, center, and right sections
        with ui.row().classes("justify-between items-center w-full"):
            # Left-aligned section/Data in row 1
            with ui.column().classes("flex-1 text-left"):
                # > link
                with ui.row().classes(f"items-center {Config.gap}"):
                    ui.icon("badge").classes(
                        "text-gray-500 text-lg"
                    )  # Add spacing after the icon
                    ui.link(
                        f"{data.get('agent', {}).get('id', 'none')}",
                        f"/agent/{data.get('agent', {}).get('id', 'none')}",
                    ).classes(f"{Config.link} text-xl")

                # Add icons to each label
                with ui.row().classes("items-center mb-1"):
                    ui.icon("computer").classes("text-gray-500 text-lg mr-1")
                    ui.label(f"OS: {data.get('system', {}).get('os', 'none')}").classes(
                        "mb-1"
                    )
                with ui.row().classes("items-center mb-1"):
                    ui.icon("dns").classes("text-gray-500 text-lg mr-1")
                    ui.label(
                        f"HostName: {data.get('system', {}).get('hostname', 'none')}"
                    ).classes("mb-1")
                with ui.row().classes("items-center mb-1"):
                    ui.icon("dns").classes("text-gray-500 text-lg mr-1")
                    ui.label(
                        f"IP: {data.get('network', {}).get('internal_ip', 'none')}"
                    ).classes("mb-1")

            # Center-aligned section/data in row 2
            with ui.column().classes("flex-1 text-center"):
                # Adds an empty row for consistency. could use for headers
                with ui.row().classes("items-center mb-1"):
                    # ui.icon("chevron_right").classes(
                    #     "text-gray-500 text-lg mr-1"
                    # )
                    ui.label("").classes("text-gray-500 text-sm mb-2")
                with ui.row().classes("items-center mb-1"):
                    ui.icon("chevron_right").classes("text-gray-500 text-lg mr-1")
                    ui.label(
                        f"External IP: {data.get('network', {}).get('external_ip', 'none')}"
                    ).classes("mb-1")
                with ui.row().classes("items-center mb-1"):
                    ui.icon("chevron_right").classes("text-gray-500 text-lg mr-1")
                    ui.label(
                        f"Geo: {data.get('geo', {}).get('city', 'none')}, {data.get('geo', {}).get('country', 'none')}"
                    ).classes("mb-1")
                with ui.row().classes("items-center mb-1"):
                    ui.icon("chevron_right").classes("text-gray-500 text-lg mr-1")
                    ui.label(
                        f"ConfigFile: {data.get('config', {}).get('file', 'none')}"
                    ).classes("mb-1")

            # Right-aligned section/data in row 3
            with ui.column().classes("flex-1 text-right"):
                # Adds an empty row for consistency. could use for headers
                with ui.row().classes("items-center mb-1"):
                    # ui.icon("chevron_right").classes(
                    #     "text-gray-500 text-lg mr-1"
                    # )
                    ui.label("").classes("text-gray-500 text-sm mb-2")
                with ui.row().classes("items-center mb-1 justify-end"):
                    ui.icon("chevron_right").classes("text-gray-500 text-lg mr-1")
                    ui.label(f"OTHERDATA").classes("mb-1")
                with ui.row().classes("items-center mb-1 justify-end"):
                    ui.icon("chevron_right").classes("text-gray-500 text-lg mr-1")
                    ui.label(f"OTHERDATA").classes("mb-1")
                with ui.row().classes("items-center mb-1 justify-end"):
                    ui.icon("chevron_right").classes("text-gray-500 text-lg mr-1")
                    ui.label(f"OTHERDATA").classes("mb-1")


def unknown_card(data: dict, title=None):
    """_summary_

    Args:
        data (dict): _description_
    """
    with ui.card().classes("w-full bg-gray-100 shadow-md p-4"):
        ui.label(f"{title if title else 'Unknown data from search'}:").classes(
            f"text-xl"
        )
        ui.markdown(f"`{data}`")


def listener_card(data: dict):
    """Cards suited for Agent cards.

    Args:
        data (dict): dict containing agent data from server
    """
    # Full-width card
    with ui.card().classes("w-full bg-gray-100 shadow-md p-4"):
        # Create a row with left, center, and right sections
        with ui.row().classes("justify-between items-center w-full"):
            # Left-aligned section/Data in row 1
            with ui.column().classes("flex-1 text-left"):
                # > link
                with ui.row().classes(f"items-center {Config.gap}"):
                    ui.icon("badge").classes(
                        "text-gray-500 text-lg"
                    )  # Add spacing after the icon
                    ui.link(
                        f"{data.get('listener', {}).get('id', 'none')} - {data.get('listener', {}).get('name', 'none')}",
                        "/#",
                    ).classes(f"{Config.link} text-xl")
                with ui.row().classes("items-center mb-1 justify-end"):
                    ui.icon("chevron_right").classes("text-gray-500 text-lg mr-1")
                    ui.label(
                        f"Address: {data.get('network', {}).get('address', 'none')}"
                    ).classes("mb-1")

            # Center-aligned section/data in row 2
            with ui.column().classes("flex-1 text-center"):
                # Adds an empty row for consistency. could use for headers
                with ui.row().classes("items-center mb-1"):
                    # ui.icon("chevron_right").classes(
                    #     "text-gray-500 text-lg mr-1"
                    # )
                    ui.label("").classes("text-gray-500 text-sm mb-2")
                with ui.row().classes("items-center mb-1 justify-end"):
                    ui.icon("chevron_right").classes("text-gray-500 text-lg mr-1")
                    ui.label(
                        f"Port: {data.get('network', {}).get('port', 'none')}"
                    ).classes("mb-1")

            # Right-aligned section/data in row 3
            with ui.column().classes("flex-1 text-right"):
                # Adds an empty row for consistency. could use for headers
                with ui.row().classes("items-center mb-1"):
                    # ui.icon("chevron_right").classes(
                    #     "text-gray-500 text-lg mr-1"
                    # )
                    ui.label("").classes("text-gray-500 text-sm mb-2")

                with ui.row().classes("items-center mb-1 justify-end"):
                    ui.icon("chevron_right").classes("text-gray-500 text-lg mr-1")
                    ui.label(
                        f"Protocol: {data.get('network', {}).get('protocol', 'none')}"
                    ).classes("mb-1")
