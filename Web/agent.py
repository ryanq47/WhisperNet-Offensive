from nicegui import ui, app
import asyncio
import requests
from cards import agent_card, unknown_card

from config import Config, ThemeConfig


class AgentView:
    """
    Individual agent view
    """

    def __init__(self, agent_id: str = None):
        self.agent_id = str(agent_id)

        self.request_data = api_call(
            url=f"{Config.API_HOST}/stats/agent/{self.agent_id}"
        )

        data = self.request_data.get("data", {})
        first_key = next(iter(data))  # Get the first key dynamically
        self.agent_data = data.get(first_key, {})
        # print(type(self.agent_data))
        # print(self.agent_data)
        # puts the data so you can access with self.agent_data["data"]["system"]["hostname"]

    # ------------------------------------------------------------------------
    #                      Render
    # ------------------------------------------------------------------------

    def render(self):
        current_settings = app.storage.user.get("settings", {})

        # fun bug: Everything still works tho???
        #   File "/home/kali/Documents/GitHub/WN-NewWeb/agent.py", line 23, in render
        #     self.agent_data.get("data", {})
        #     ^^^^^^^^^^^^^^^^^^^
        # AttributeError: 'str' object has no attribute 'get'

        hostname = (
            self.agent_data.get("data", {})
            .get("system", {})
            .get("hostname", "Unknown Hostname")
        )

        # with ui.header().classes(replace='row items-center').classes('bg-neutral-800') as header:
        # ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
        with ui.row().classes("text-5xl"):
            ui.icon("computer")
            ui.label(str(hostname)).classes("h-10  600")
        # reduce space here
        with ui.row().classes("w-full text-2xl"):
            ui.icon("badge")
            ui.label(self.agent_id).classes("h-6  400")
            ui.space()
            ui.icon("timer")
            ui.label("Last Checkin: 01:01:01 ").classes("h-6  400")

        ui.separator()
        with ui.tabs() as tabs:
            ui.tab("MAIN")
            # ui.tab('OTHER')

            # DEV Tabs - can do one if per tab if you want to maintain an order
            if current_settings.get("Dev Mode", False):
                ui.tab(
                    "STATS"
                )  # Graphs N Stuff? There's examples of this in nicegui examples
                # ui.tab('FileExplorer')
                ui.tab("SHELL")
                ui.tab("NOTES")

        with ui.tab_panels(tabs, value="MAIN").classes("w-full border"):
            with ui.tab_panel("MAIN"):
                # ui.label('Content of A')
                self.render_main_tab()

            if current_settings.get("Dev Mode", False):
                with ui.tab_panel("STATS"):
                    # ui.label('Content of A')
                    self.render_stats_tab()

            if current_settings.get("Dev Mode", False):
                with ui.tab_panel("SHELL"):
                    # ui.label('Content of A')
                    self.render_shell_tab()

            if current_settings.get("Dev Mode", False):
                with ui.tab_panel("NOTES"):
                    # ui.label('Content of A')
                    self.render_notes_tab()

    # ------------------------------------------------------------------------
    #                      Main Tab
    # ------------------------------------------------------------------------

    def render_main_tab(self):
        current_settings = app.storage.user.get("settings", {})

        with ui.row().classes("w-full h-full flex"):
            # Details Section
            with ui.column().classes("flex-1 h-full"):
                with ui.row().classes("items-center justify-between w-full"):
                    ui.label("Details").classes("h-6  400")
                ui.separator()
                create_ui_from_json(self.agent_data)

            # Command History Section
            with ui.column().classes("flex-1 h-full"):
                aggrid_theme = (
                    "ag-theme-balham-dark"
                    if current_settings.get("Dark Mode", False)
                    else "ag-theme-balham"
                )
                # Header for Command History
                ui.label("Command History").classes("h-6  400")
                ui.separator()

                mydict = []
                for i in range(1, 100):
                    mydict.append(
                        {"command": "exec:powershell:whoami", "result": "bob_boberson"}
                    )

                # Unique command for testing
                mydict.append(
                    {"command": "exec:powershell:whoami /all", "result": "john_doe"}
                )

                self.command_grid = (
                    ui.aggrid(
                        {
                            "columnDefs": [
                                {
                                    "headerName": "Timestamp",
                                    "field": "timestamp",
                                    "filter": "agTextColumnFilter",
                                    "floatingFilter": True,
                                },
                                {
                                    "headerName": "Command",
                                    "field": "command",
                                    "filter": "agTextColumnFilter",
                                    "floatingFilter": True,
                                },
                                {
                                    "headerName": "Result",
                                    "field": "result",
                                    "filter": "agTextColumnFilter",
                                    "floatingFilter": True,
                                },
                            ],
                            "rowData": mydict,  # Pass the list as rowData
                        }
                    )
                    .style("height: 750px")
                    .classes(f"{aggrid_theme}")
                )

                # Full-width Button: Below Command History section
                ui.button(
                    "Export",
                    on_click=lambda: self.command_grid.run_grid_method(
                        "exportDataAsCsv"
                    ),
                ).props("auto flat").classes("w-full py-2 mt-2")

    # ------------------------------------------------------------------------
    #                      Stats Tab
    # ------------------------------------------------------------------------

    def render_stats_tab(self):
        with ui.row().classes("w-full h-full flex"):
            with ui.row().classes("flex-1 h-full"):
                ui.label("Test Graph - Average Checkin Times").classes("h-6  400")
                fig = {
                    "data": [
                        {
                            "type": "scatter",
                            "name": "Trace 1",
                            "x": [1, 2, 3, 4],
                            "y": [1, 2, 3, 2.5],
                        },
                        {
                            "type": "scatter",
                            "name": "Trace 2",
                            "x": [1, 2, 3, 4],
                            "y": [1.4, 1.8, 3.8, 3.2],
                            "line": {"dash": "dot", "width": 3},
                        },
                    ],
                    "layout": {
                        "margin": {"l": 15, "r": 0, "t": 0, "b": 15},
                        "plot_bgcolor": "#E5ECF6",
                        "xaxis": {"gridcolor": "white"},
                        "yaxis": {"gridcolor": "white"},
                    },
                }
                ui.plotly(fig).classes("w-full h-40")
                ui.plotly(fig).classes("w-full h-40")
                ui.plotly(fig).classes("w-full h-40")
                ui.plotly(fig).classes("w-full h-40")

    def render_shell_tab(self):
        with ui.row().classes("w-full h-full flex items-center justify-center"):
            self.search_field = (
                ui.input(placeholder="Command...")
                .props('autofocus outlined item-aligned input-class="ml-3"')
                .classes("w-full mt-24 transition-all")
            )

    def render_notes_tab(self):
        ...
        # with ui.row().classes('w-full h-full flex'):
        #     # Move to somethign server based, or find a better way to save these session wise?
        #     ui.textarea('User notes. NOTE! These are stored in the current session, aka only YOU can see these, in this browser. THEY WILL DISAPPEAR ON DIFFERENT BROWSERS - Fix This to have a notes endpoint for agents + save, etc').classes('w-full').bind_value(app.storage.user, 'note')


class AgentsView:
    """
    A list of agents
    """

    def __init__(self):

        self.request_data = api_call(url=f"{Config.API_HOST}/stats/agents")

        # get top level data key from response
        self.request_data = self.request_data.get("data", {})

    def render(self):
        self.render_agents_grid()

    def render_agents_grid(self):
        try:
            current_settings = app.storage.user.get("settings", {})
            # NOTES:
            #     Holy Shitballs aggrids are so much fun -_-

            #     I originally had a similar setupto the /search here, but that didn't include granular filtering.
            #     As for URL's, I had to render an HTML element in the Agent ID field. It's a little weird,
            #     as I can't use ui.navigate.to, so the whole path has to go into it. Currently hardocded,
            #     will be fixed later

            # Extract the relevant data
            agents = self.request_data
            row_data = []
            for key, agent_info in agents.items():
                agent_id = agent_info.get("agent_id", "Unknown")
                hostname = agent_info["data"]["system"].get("hostname", "Unknown")
                os = agent_info["data"]["system"].get("os", "Unknown")
                internal_ip = agent_info["data"]["network"].get(
                    "internal_ip", "Unknown"
                )
                last_seen = agent_info["data"]["agent"].get("last_seen", "Unknown")

                # Append formatted row
                print(
                    "WARNING: Path busted with clickable aggrid, doesn't work outside of localhost"
                )
                row_data.append(
                    {
                        "Agent ID": f"<u><a href='/agent/{agent_id}'>{agent_id}</a></u>",
                        "Hostname": hostname,
                        "OS": os,
                        "Internal IP": internal_ip,
                        "Last Seen": last_seen,
                    }
                )

            # Render the aggrid
            with ui.element().classes("gap-0 w-full"):
                aggrid_theme = (
                    "ag-theme-balham-dark"
                    if current_settings.get("Dark Mode", False)
                    else "ag-theme-balham"
                )
                ui.aggrid(
                    {
                        "domLayout": "autoHeight",
                        "columnDefs": [
                            {
                                "headerName": "Agent ID",
                                "field": "Agent ID",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                            },
                            {
                                "headerName": "Hostname",
                                "field": "Hostname",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                            },
                            {
                                "headerName": "OS",
                                "field": "OS",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                            },
                            {
                                "headerName": "Internal IP",
                                "field": "Internal IP",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                            },
                            {
                                "headerName": "Last Seen",
                                "field": "Last Seen",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                            },
                        ],
                        "rowData": row_data,
                    },
                    html_columns=[0],
                ).style("height: 750px").classes(f"{aggrid_theme}")
        except Exception as e:
            print(f"Error rendering grid: {e}")


# ------------------------------------------------------------------------
#                      Network Stuff
# ------------------------------------------------------------------------


def api_call(url, timeout=3):
    """
    Makes a synchronous GET request to the specified URL and returns the JSON response.

    Args:
        url (str): The URL to request.
        timeout (int): The timeout for the request in seconds (default: 3).

    Returns:
        dict: Parsed JSON response from the server.

    Raises:
        ValueError: If the response cannot be parsed as JSON.
        requests.RequestException: For network-related errors or timeouts.
    """
    if not url:
        raise ValueError("A valid URL must be provided.")

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raise an error for HTTP errors (4xx/5xx)
        return response.json()  # Parse and return the JSON response
    except requests.JSONDecodeError:
        raise ValueError("The response is not valid JSON.")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        raise  # Re-raise the exception for the caller to handle


# ------------------------------------------------------------------------
#                      Misc Stuff
# ------------------------------------------------------------------------


# Recursive function to create UI elements based on JSON
def create_ui_from_json(json_data, parent=None):
    for key, value in json_data.items():
        # Add label for the key with bullet point
        with ui.column() if parent is None else parent:
            if isinstance(value, dict):
                # Bold key for better visibility
                ui.label(f"• {key}:").style("font-weight: bold; font-size: 1.1em;")

                # Recursively handle nested dictionaries with indentation
                with ui.column().style(
                    "margin-left: 20px; padding-left: 10px; border-left: 2px solid #ccc;"
                ):
                    create_ui_from_json(value)
            else:
                # Add value with bullet point and bolded key
                ui.label(f"• {key}: {value}").style("font-size: 1em;")
