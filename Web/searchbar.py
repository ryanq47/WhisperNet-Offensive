#!/usr/bin/env python3
import asyncio
from typing import Optional
from config import Config
import httpx
from nicegui import events, ui
import time
import json

# Works fine, error on server end with getting all data out, see bug in github.

api = httpx.AsyncClient()
running_query: Optional[asyncio.Task] = None


class Search:
    def __init__(self):
        self.search_field = None

    def spawn_search_bar(self):
        print("LOADING SEARCH - NEW CLASS INSTANCE")

        self.search_field = (
            ui.input(on_change=self.search)
            .props('autofocus outlined item-aligned input-class="ml-3"')
            .classes("w-1/2 self-center mt-24 transition-all")
        )
        self.results = ui.row()

    async def search(self, e: events.ValueChangeEventArguments) -> None:
        """Search for cocktails as you type."""
        global running_query
        if running_query:
            running_query.cancel()
        self.search_field.classes("mt-2", remove="mt-24")
        self.results.clear()

        # do this 2 times for agents, listeners? or have one big endpoint?
        # or a search endpoint?
        running_query = asyncio.create_task(
            api.get(
                # f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={e.value}"
                "http://127.0.0.1:8081/stats/all"
            )
        )
        response = await running_query
        if response.text == "":
            return

        # if if/else tree gets too big, switch to dispatch/dict method
        with self.results:
            start_time = time.time()  # Start the timer

            print(f"Search Term: {e.value}")
            # search ONLY in data key for accurate results
            try:
                response_data = response.json()["data"]
            # print(response_data)
            except Exception as e:
                unknown_card(
                    response.json(),
                    title="Could not find 'data' subkey in received json",
                )
                print(e)
                return

            # Iterate over each dynamic key and its corresponding value
            for data_key, response_data in response_data.items():
                try:
                    # Convert values to lowercase strings for search comparison
                    response_data_values = (
                        str(value).lower() for value in response_data["data"].values()
                    )

                    # Check if the search term is in any value
                    if any(e.value.lower() in value for value in response_data_values):
                        # Check if it's an agent
                        if "agent" in data_key:
                            agent_card(data=response_data)
                        # Check if it's a listener
                        elif (
                            "listener" in data_key
                        ):  # Replace 'someOtherKey' with actual key
                            listener_card(data=response_data)
                        else:
                            unknown_card(data=response_data)

                    # Wildcard search (match all entries)
                    elif e.value == "*" or e.value == "" or e.value == None:
                        # Check if it's an agent
                        if "agent" in data_key:
                            agent_card(data=response_data)
                        # Check if it's a listener
                        elif (
                            "listener" in data_key
                        ):  # Replace 'someOtherKey' with actual key
                            listener_card(data=response_data)
                        else:
                            unknown_card(data=response_data)
                except Exception as e:
                    unknown_card(response_data)
                    print(e)
                    continue

            end_time = time.time()  # End the timer
            print(f"Execution Time: {end_time - start_time:.4f} seconds")
            ui.notify(f"Execution Time: {end_time - start_time:.4f} seconds")
        running_query = None


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
