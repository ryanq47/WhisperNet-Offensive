from nicegui import ui, app
import asyncio
import requests


class AgentView:
    def __init__(self, agent_id: str = None):
        self.agent_id = str(agent_id)

        self.request_data = api_call(
            url=f"http://127.0.0.1:8081/stats/agent/{self.agent_id}"
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
            ui.label(str(hostname)).classes("h-10 text-slate-600")
        # reduce space here
        with ui.row().classes("w-full text-2xl"):
            ui.icon("badge")
            ui.label(self.agent_id).classes("h-6 text-slate-400")
            ui.space()
            ui.icon("timer")
            ui.label("Last Checkin: 01:01:01 ").classes("h-6 text-slate-400")

        ui.separator()
        with ui.tabs() as tabs:
            ui.tab("MAIN")
            # ui.tab('OTHER')
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
            with ui.tab_panel("STATS"):
                # ui.label('Content of A')
                self.render_stats_tab()
            with ui.tab_panel("SHELL"):
                # ui.label('Content of A')
                self.render_shell_tab()
            with ui.tab_panel("NOTES"):
                # ui.label('Content of A')
                self.render_notes_tab()

    # ------------------------------------------------------------------------
    #                      Main Tab
    # ------------------------------------------------------------------------

    def render_main_tab(self):
        with ui.row().classes("w-full h-full flex"):
            # Details Section
            with ui.column().classes("flex-1 h-full"):
                with ui.row().classes("items-center justify-between w-full"):
                    ui.label("Details").classes("h-6 text-slate-400")
                ui.separator()
                create_ui_from_json(self.agent_data)

            # Command History Section
            with ui.column().classes("flex-1 h-full"):
                # Header for Command History
                ui.label("Command History").classes("h-6 text-slate-400")
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

                self.command_grid = ui.aggrid(
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
                ).style(
                    "height: 750px"
                )  # .classes("h-64")

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
                ui.label("Test Graph - Average Checkin Times").classes(
                    "h-6 text-slate-400"
                )
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
