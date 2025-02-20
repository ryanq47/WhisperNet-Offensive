from nicegui import ui, app
import asyncio
import requests
from cards import agent_card, unknown_card
from config import Config, ThemeConfig
from build import BuildView
from navbar import *
from networking import api_call, api_post_call, api_delete_call
from scripts import ScriptsView
from nicegui.events import KeyEventArguments


# ---------------------------
#   UI Helper Function
# ---------------------------
def create_ui_from_json(json_data, parent=None):
    """
    Recursively creates UI elements from a JSON/dict structure.
    """
    for key, value in json_data.items():
        with ui.column() if parent is None else parent:
            if isinstance(value, dict):
                ui.label(f"• {key}:").style("font-weight: bold; font-size: 1.1em;")
                with ui.column().style(
                    "margin-left: 20px; padding-left: 10px; border-left: 2px solid #ccc;"
                ):
                    create_ui_from_json(value)
            else:
                ui.label(f"• {key}: {value}").style("font-size: 1em;")


# ---------------------------
#   Agent View
# ---------------------------
class AgentView:
    """
    Displays detailed information about an individual agent.
    """

    def __init__(self, agent_id: str = None):
        self.agent_id = str(agent_id)
        self.request_data = api_call(url=f"/stats/agent/{self.agent_id}")
        data = self.request_data.get("data", {})
        first_key = next(iter(data))
        self.agent_data = data.get(first_key, {})

    def render(self):
        """
        Renders the complete agent view including header, tabs, and tab panels.
        """
        with ui.element().classes("w-full h-full"):

            current_settings = app.storage.user.get("settings", {})

            # Tabs Section
            with ui.tabs() as tabs:
                ui.tab("MAIN")
                ui.tab("SHELL")

                if current_settings.get("Dev Mode", False):
                    ui.tab("STATS")
                    ui.tab("NOTES")

            # Tab Panels Container – note the explicit h-full for proper expansion.
            with ui.tab_panels(tabs, value="MAIN").classes("w-full h-full border"):
                with ui.tab_panel("MAIN").classes("h-full"):
                    self.render_main_tab()
                with ui.tab_panel("SHELL").classes("h-full"):
                    self.render_shell_tab()
                if current_settings.get("Dev Mode", False):
                    with ui.tab_panel("STATS").classes("h-full"):
                        self.render_stats_tab()
                # if current_settings.get("Dev Mode", False):

                if current_settings.get("Dev Mode", False):
                    with ui.tab_panel("NOTES").classes("h-full"):
                        self.render_notes_tab()

    def render_main_tab(self):
        """
        Renders the MAIN tab with agent details and command history grid.
        """

        # Agent Header Section
        hostname = (
            self.agent_data.get("data", {})
            .get("system", {})
            .get("hostname", "Unknown Hostname")
        )
        with ui.row().classes("text-5xl"):
            ui.icon("computer")
            ui.label(str(hostname)).classes("h-10")
        with ui.row().classes("w-full text-2xl"):
            ui.icon("badge")
            ui.label(self.agent_id).classes("h-6")
            ui.space()
            ui.icon("timer")
            ui.label("Last Checkin: 01:01:01").classes("h-6")
        ui.separator()

        current_settings = app.storage.user.get("settings", {})
        with ui.row().classes("w-full h-full flex"):
            # Left: Agent details.

            with ui.column().classes("flex-1 h-full"):
                with ui.row().classes("items-center justify-between w-full"):
                    ui.label("Details").classes("h-6")
                ui.separator()
                with ui.scroll_area().classes("h-full"):
                    create_ui_from_json(self.agent_data)

            # Right: Command history grid.
            with ui.column().classes("flex-1 h-full"):
                aggrid_theme = (
                    "ag-theme-balham-dark"
                    if current_settings.get("Dark Mode", False)
                    else "ag-theme-balham"
                )
                ui.label("Command History - refresh page to refresh me").classes("h-6")
                ui.separator()

                # Get the data
                data_list = api_call(url=f"/agent/{self.agent_id}/command/all").get(
                    "data", []
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
                                "headerName": "Response",
                                "field": "response",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                            },
                        ],
                        "rowData": data_list,
                    }
                ).classes(f"{aggrid_theme} h-full")

                ui.button(
                    "Export",
                    on_click=lambda: self.command_grid.run_grid_method(
                        "exportDataAsCsv"
                    ),
                ).props("auto flat").classes("w-full py-2 mt-2")

    def render_stats_tab(self):
        """
        Renders the STATS tab with sample graphs.
        """
        with ui.row().classes("w-full h-full flex"):
            with ui.row().classes("flex-1 h-full"):
                ui.label("Test Graph - Average Checkin Times").classes("h-6")
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
                # Render multiple plots.
                for _ in range(4):
                    ui.plotly(fig).classes("w-full h-40")

    def render_shell_tab(self):
        """
        Renders the SHELL tab with a scrollable command history and an input area.
        Auto-refresh occurs every second.
        """
        # Attributes for auto-scroll behavior.
        self.shell_container = None
        self.auto_scroll_enabled = True

        def handle_keydown(e):
            # Access the key from e.args dictionary
            key = e.args.get("key")
            # Check if the Enter key was pressed
            if key == "Enter":
                # e.prevent_default()  # Prevents newline in textarea
                send_command()

        def update_scripts_options():
            # move into dedicated func
            # kinda tall - but script selection
            # get valid scripts
            # api_call("script list api")
            # need to get current script as well, and put in this value so user doenst get confused
            # on refresh
            # Fetch the API response
            response = api_call(url=f"/scripts/files")

            # Extract script data properly
            scripts_data = (
                [
                    script.get("filename", "Unknown Script")
                    for script in response.get("data", [])
                ]
                if response.get("data")
                else ["No Scripts Available"]
            )

            # Populate the UI dropdown
            # on change... trigger API call to select a script.
            # /agents/uuid/script (POST req, takes script name)
            script_selector = ui.select(
                options=scripts_data,
                label="Extension Scripts",
                on_change=lambda e: update_script(script_selector.value),
            ).classes("w-full")

        def update_script(script_name):
            data = {"command_script": script_name}

            api_post_call(
                url=f"/agent/{self.agent_id}/command-script/register", data=data
            )
            ui.notify("Updated script on agent", position="top-right")

        def on_scroll(e):
            # Disable auto-scroll if the user scrolls away from the bottom.
            self.auto_scroll_enabled = e.vertical_percentage >= 0.95

        def update_shell_data():
            data = api_call(url=f"/agent/{self.agent_id}/command/all").get("data", [])

            # shitty bug fix for if there's no command data from the client
            # otherwise it 500's
            if not data:
                pass
                # ui.label("No command history yet...")
            else:
                # Sort entries so that older entries are first.
                data.sort(key=lambda entry: entry.get("timestamp", ""))
                if self.shell_container is not None:
                    self.shell_container.clear()
                    with self.shell_container:
                        for entry in data:
                            cmd = entry.get("command", "")
                            ui.markdown(f"> {cmd}").style("font-family: monospace")
                            response_value = entry.get("response")
                            if response_value:
                                ui.label(response_value).style(
                                    "white-space: pre; font-family: monospace;"
                                )
                            else:
                                # not using animation at the moment due to the way the shell refreshes/updates
                                ui.skeleton(animation="none").style(
                                    "width: 50%; height: 1.2em; margin: 4px 0;"
                                )
                    if self.auto_scroll_enabled:
                        self.shell_container.scroll_to(percent=1.0)

        def send_command():
            api_post_call(
                url=f"/agent/{self.agent_id}/command/enqueue",
                data={"command": command_input.value},
            )
            command_input.value = ""
            update_shell_data()

        # update the script options
        update_scripts_options()

        # Shell tab layout: Fill parent container (using h-full).
        with ui.column().classes(
            "h-full w-full flex flex-col"
        ):  # bg-gray-900 text-white f
            # Command History Area:
            with ui.row().classes("grow w-full p-4"):
                with ui.scroll_area(on_scroll=on_scroll).classes(
                    "w-full h-full border  rounded-lg p-2"  # border-gray-700
                ) as self.shell_container:
                    # The shell command history will be dynamically added here.
                    pass
            # Command Input Area:
            with ui.row().classes("w-full items-center p-4"):
                command_input = (
                    ui.textarea(placeholder="Type a command...")
                    .props('autofocus outlined input-class="ml-3" input-class=h-12')
                    .classes("text-black grow mr-4")
                    .on(
                        "keydown", handle_keydown
                    )  # handle keydown here cuz nested functions
                )
                ui.button("Send Command", on_click=send_command).classes("w-32")
        update_shell_data()
        ui.timer(interval=1.0, callback=update_shell_data)

    def render_notes_tab(self):
        """
        Renders the NOTES tab (placeholder for user notes).
        """
        ui.textarea(
            "User notes. NOTE: These are stored in your session and will disappear on a new browser session."
        ).classes("w-full").bind_value(app.storage.user, "note")


# ---------------------------
#   Agents List View
# ---------------------------
class AgentsView:
    """
    Displays a list of agents.
    """

    def __init__(self):
        self.request_data = api_call(url=f"/stats/agents")
        self.request_data = self.request_data.get("data", {})

    def render(self):
        self.render_agents_grid()

    def render_agents_grid(self):
        try:
            current_settings = app.storage.user.get("settings", {})
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
                row_data.append(
                    {
                        "Agent ID": f"<u><a href='/agent/{agent_id}'>{agent_id}</a></u>",
                        "Hostname": hostname,
                        "OS": os,
                        "Internal IP": internal_ip,
                        "Last Seen": last_seen,
                    }
                )
            with ui.column().classes("w-full h-full overflow-auto"):
                aggrid_theme = (
                    "ag-theme-balham-dark"
                    if current_settings.get("Dark Mode", False)
                    else "ag-theme-balham"
                )
                ui.aggrid(
                    {
                        "columnDefs": [
                            {
                                "headerName": "Agent ID",
                                "field": "Agent ID",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 225,
                            },
                            {
                                "headerName": "Hostname",
                                "field": "Hostname",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 225,
                            },
                            {
                                "headerName": "OS",
                                "field": "OS",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 225,
                            },
                            {
                                "headerName": "Internal IP",
                                "field": "Internal IP",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 150,
                            },
                            {
                                "headerName": "Last Seen",
                                "field": "Last Seen",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 225,
                            },
                        ],
                        "rowData": row_data,
                    },
                    html_columns=[0],
                ).classes(f"{aggrid_theme} w-full h-full")
        except Exception as e:
            print(f"Error rendering grid: {e}")


class AgentsPage:
    def __init__(self): ...

    def render(self):
        with ui.column().classes("w-full h-full p-[10px]"):
            # HEADER 1
            with ui.row().classes("w-full text-5xl"):
                ui.icon("computer")
                ui.label("Agents").classes("h-10")

            # HEADER 2
            with ui.row().classes("w-full text-2xl"):
                ui.icon("construction")
                ui.label("Monitor, Access, and Build Agent binaries").classes("h-6")
                ui.space()
            ui.separator()

            # -- TABS --
            with ui.tabs() as tabs:
                ui.tab("Agents")
                ui.tab("Binaries + Builder")
                ui.tab("Scripts")

            # -- TAB PANELS --
            with ui.tab_panels(tabs, value="Agents").classes("w-full h-full border"):
                with ui.tab_panel("Agents").classes("h-full"):
                    a = AgentsView()
                    a.render()
                with ui.tab_panel("Binaries + Builder"):
                    a = BuildView()
                    a.render()
                with ui.tab_panel("Scripts"):
                    a = ScriptsView()
                    a.render()
