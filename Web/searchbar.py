#!/usr/bin/env python3
import asyncio
from typing import Optional
from config import ThemeConfig
import httpx
from nicegui import events, ui, app
import time
import json
from cards import agent_card, unknown_card, listener_card
from config import Config, ThemeConfig

# Works fine, error on server end with getting all data out, see bug in github.

api = httpx.AsyncClient()
running_query: Optional[asyncio.Task] = None


class Search:
    def __init__(self, vertical_padding=True, full_horizontal_width=False, query=None):
        self.search_field = None

        # docstring this, vertical pading for searchbar, used in search tab
        self.vertical_padding = vertical_padding

        # width for serachbar
        self.full_horizontal_width = full_horizontal_width

        self.query = query

    def spawn_search_bar(self):
        ui.label(
            "NOTE: Dedicated search with no aggrid/grid due to mutliple data types here"
        )
        print("LOADING SEARCH - NEW CLASS INSTANCE")

        if self.vertical_padding:
            self.search_field = (
                ui.input(on_change=self.search)
                .props('autofocus outlined item-aligned input-class="ml-3"')
                .classes("w-1/2 self-center mt-24 transition-all")
            )
            self.results = ui.row()

        else:
            self.search_field = (
                ui.input(on_change=self.search)
                .props('autofocus outlined item-aligned input-class="ml-3"')
                .classes(
                    f"{"w-full" if self.full_horizontal_width else "w-1/2"}  self-center transition-all"
                )
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
                f"{Config.API_HOST}/stats/all"
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
