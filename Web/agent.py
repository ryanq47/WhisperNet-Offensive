from nicegui import ui, app
import asyncio
import requests
from cards import agent_card, unknown_card
from config import Config, ThemeConfig
from build import BuildView, ShellcodeBuildView
from navbar import *
from networking import api_call, api_post_call, api_delete_call
from scripts import ScriptsView
from nicegui.events import KeyEventArguments

# ---------------------------
#   Easy Settings
# ---------------------------

SHELL_SCROLL_DURATION = (
    0.25  # really just speed, how long it takes for the "scroll animation" to complete
)


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
        self.check_new_status()

    def check_new_status(self):
        # On click of agent, if not new, send a "not new" to the server
        if self.agent_data.get("data", {}).get("agent").get("new"):
            ui.notify(
                "Agent clicked into, no longer considered new", position="top-right"
            )
            data = {"new": False}
            # async this?
            # api_post_call(f"/agent/{self.agent_id}/new", data=data)
            api_post_call(f"/agent/{self.agent_id}/new", data=data)

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

            # Tab Panels Container – note the explicit h-full for proper expansion.
            with ui.tab_panels(tabs, value="MAIN").classes("w-full h-full border"):
                with ui.tab_panel("MAIN").classes("h-full"):
                    self.render_main_tab()
                with ui.tab_panel("SHELL").classes("h-full"):
                    self.render_shell_tab()
                # if current_settings.get("Dev Mode", False):
                #     with ui.tab_panel("STATS").classes("h-full"):
                #         self.render_stats_tab()
                # if current_settings.get("Dev Mode", False):

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
        last_seen = self.agent_data["data"]["agent"].get("last_seen", "Unknown")

        with ui.row().classes("text-5xl"):
            ui.icon("computer")
            ui.label(str(hostname)).classes("h-10")
        with ui.row().classes("w-full text-2xl"):
            ui.icon("badge")
            ui.label(self.agent_id).classes("h-6")
            ui.space()
            ui.icon("timer")

            ui.label(f"Last Seen: {last_seen}").classes("h-6")
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
                        "exportDataAsCsv",
                        {"fileName": f"{self.agent_id}_command_history.csv"},
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
        # Enable auto-scroll when near the bottom.
        self.auto_scroll_enabled = True
        # Keep track of which command entries have been appended.
        self.known_command_ids = {}

        # and finally, render the script options
        self.render_scripts_options()

        async def handle_keydown(e):
            # Trigger send_command on Enter key.
            if e.args.get("key") == "Enter":
                await send_command()

        # fix: get current script. If current script is none, put "no script selected" on selector.
        # additionally, break it out a bit, it's annoyingly duct taped together

        def on_scroll(e):
            # If the user scrolls away from the bottom, disable auto-scroll.
            self.auto_scroll_enabled = e.vertical_percentage >= 0.95

        def update_shell_data():
            data = api_call(url=f"/agent/{self.agent_id}/command/all").get("data", [])
            if not data:
                return

            # Sort entries chronologically.
            data.sort(key=lambda entry: entry.get("timestamp", ""))
            for entry in data:
                # Use a unique identifier for the command.
                cmd_id = entry.get("command_id", "")
                if not cmd_id:
                    cmd_id = f"no_id_{entry.get('timestamp', '')}"
                cmd = entry.get("command", "")
                response_value = entry.get("response") or "Waiting on callback..."

                if cmd_id not in self.known_command_ids:
                    # Append new entry HTML to the output element.
                    html = (
                        f"<div id='shell_entry_{cmd_id}' style='margin-bottom: 10px;'>"
                        f"<div style='font-family: monospace;'>&gt; {cmd}</div>"
                        f"<div id='response_{cmd_id}' style='white-space: pre; font-family: monospace;'>{response_value}</div>"
                        "<hr/></div>"
                    )
                    ui.run_javascript(
                        f"document.getElementById('shell_output').insertAdjacentHTML('beforeend', {html!r});"
                    )
                    self.known_command_ids[cmd_id] = True
                else:
                    # Update an existing entry's response only if new response data is available.
                    if response_value:
                        # Update using only text node modification if no selection is active.
                        js_code = f"""
    (function() {{
    var selection = window.getSelection();
    if (!selection || selection.toString() === "") {{
        var elem = document.getElementById('response_{cmd_id}');
        if (elem && elem.firstChild) {{
        elem.firstChild.nodeValue = {response_value!r};
        }}
    }}
    }})();
    """
                        ui.run_javascript(js_code)
            # Auto-scroll if enabled.
            if self.auto_scroll_enabled:
                ui.run_javascript(
                    """
                    var el = document.getElementById('shell_output');
                    el.scrollTop = el.scrollHeight;
                """
                )

        def send_command():
            api_post_call(
                url=f"/agent/{self.agent_id}/command/enqueue",
                data={"command": command_input.value},
            )
            command_input.value = ""
            update_shell_data()

        # Initialize the script options.
        # render_scripts_options()
        # on load, load "default.py", the default scirpt
        # ducttape bug fix, if this is not called, no script is rendered, and if there's only one script, you can't select a script
        # update_script("default.py")
        # FUCK this doesn't work, script forces default.py on refresh...

        # Shell tab layout.
        with ui.column().classes("h-full w-full flex flex-col"):
            # Command History Area.
            with ui.row().classes("grow w-full p-4"):
                with ui.scroll_area(on_scroll=on_scroll).classes(
                    "w-full h-full border rounded-lg p-2"
                ):
                    # Create a single HTML element to hold the shell output.
                    ui.html(
                        "<div id='shell_output' style='white-space: pre-wrap; font-family: monospace;'>Shell Output:</div>"
                    )
            # Command Input Area.
            with ui.row().classes("w-full items-center p-4"):
                command_input = (
                    ui.textarea(placeholder="Type a command...")
                    .props('autofocus outlined input-class="ml-3" input-class="h-12"')
                    .classes("text-black grow mr-4")
                    .on("keydown", handle_keydown)
                )
                ui.button("Send Command", on_click=send_command).classes("w-32")

        # Load the initial shell data and set up the auto-refresh timer.
        update_shell_data()
        ui.timer(interval=1.0, callback=update_shell_data)

    def render_scripts_options(self):
        """
        Handles the script options.

        Checks if an agent has a script. If so, sets that to the current script on the ui.select
        If not, display's None.

        When updating a script, it calls the _register_script to update the script for the agent.


        """
        # Get the list of available scripts.
        response = api_call(url="/scripts/files")
        scripts_data = (
            [
                script.get("filename", "Unknown Script")
                for script in response.get("data", [])
            ]
            if response.get("data")
            else ["No Scripts Available"]
        )

        # with agent id, get current script.
        agent_data = api_call(url=f"/stats/agent/{self.agent_id}").get("data", {})

        # Get the inner dictionary, which holds the actual agent info. Only one agent is returned from this call, so it'll just grab the first one
        agent_info = next(iter(agent_data.values()), {})

        # Then navigate to the command_script inside the nested structure.
        agent_script = (
            agent_info.get("data", {}).get("config", {}).get("command_script")
        )

        # Create the script selector dropdown.
        ui.select(
            options=scripts_data,
            label="Extension Scripts",
            on_change=lambda e: self._register_script(e.value),
            value=agent_script,  # show the currently selected script if there is one
        ).classes("w-full")

    def _register_script(self, script_name):
        """
        POST call to update the script for an agent on the server

        script_name: The name of the script on the server

        Usually this would be under the render_scripts_options method, but ui.select needs a callback func to call on change

        Endpoint: /agent/{self.agent_id}/command-script/register

        """
        api_post_call(
            url=f"/agent/{self.agent_id}/command-script/register",
            data={"command_script": script_name},
        )
        ui.notify(f"Updated script to {script_name} on agent", position="top-right")

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

    async def open_help_dialog(self) -> None:
        """Open a help dialog with instructions for the shellcode converter."""
        with ui.dialog().classes("w-full").props("full-width") as dialog, ui.card():
            ui.markdown("# Agents Tab:")
            ui.separator()
            ui.markdown(
                """
                This is where you will find all the agents that are checking in.

                Go ahead and click on a UUID of an agent to interact with said agent.

                Blue colored agents are agents that have not been interacted with yet. This makes it easy
                to find newly connected agents.

                Pro tip: The fields will not populate until the `system_recon` command is run
                in each agent. This command is found in the `default.py` command script, in the agent shell.
                """
            )
        dialog.open()
        await dialog

    def render_help_button(self) -> None:
        """Render a help button pinned at the bottom-right of the screen."""
        help_button = ui.button("Current Page Info", on_click=self.open_help_dialog)
        help_button.style("position: fixed; top: 170px; right: 24px; ")

    def render(self):
        self.render_agents_grid()

    def render_agents_grid(self):
        try:
            self.render_help_button()
            current_settings = app.storage.user.get("settings", {})
            agents = self.request_data
            row_data = []
            for key, agent_info in agents.items():
                agent_id = agent_info.get("agent_id", "Unknown")
                hostname = agent_info["data"]["system"].get("hostname", "Unknown")
                os = agent_info["data"]["system"].get("os", "Unknown")
                notes = agent_info["data"]["agent"].get("notes", "")
                internal_ip = agent_info["data"]["network"].get(
                    "internal_ip", "Unknown"
                )
                external_ip = agent_info["data"]["network"].get(
                    "external_ip", "Unknown"
                )
                last_seen = agent_info["data"]["agent"].get("last_seen", "Unknown")
                new_agent = agent_info["data"]["agent"].get("new", False)

                row_data.append(
                    {
                        "Link Agent ID": f"<u><a href='/agent/{agent_id}'>{agent_id}</a></u>",
                        "Raw Agent ID": agent_id,
                        "Hostname": hostname,
                        "OS": os,
                        "Notes": notes,
                        "Internal IP": internal_ip,
                        "External IP": external_ip,
                        "Last Seen": last_seen,
                        "New": new_agent,  # used for cell highligthing, not currently shown in the grid itself
                    }
                )
            with ui.column().classes("w-full h-full overflow-auto"):
                aggrid_theme = (
                    "ag-theme-balham-dark"
                    if current_settings.get("Dark Mode", False)
                    else "ag-theme-balham"
                )
                self.aggrid = ui.aggrid(
                    # notes: Using per cell highlighting as it's a quick fix.
                    # it's apparently possible to do it for the whole thing, I'll get to that later
                    {
                        "columnDefs": [
                            {
                                "headerName": "",
                                "checkboxSelection": True,
                                "headerCheckboxSelection": True,
                                "width": 50,
                                "pinned": "left",
                                "floatingFilter": True,
                                "cellClassRules": {
                                    "bg-blue-500": "data.New"  # use the New field that is in the aggrid data
                                },
                            },
                            {
                                "headerName": "Link Agent ID",
                                "field": "Link Agent ID",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 225,
                                "cellClassRules": {"bg-blue-500": "data.New"},
                            },
                            {  # used for storing JUST the agent ID, without HTML stuff
                                "headerName": "Raw Agent ID",
                                "field": "Raw Agent ID",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 225,
                                "hide": True,
                                "cellClassRules": {"bg-blue-500": "data.New"},
                            },
                            {
                                "headerName": "Hostname",
                                "field": "Hostname",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 225,
                                "cellClassRules": {"bg-blue-500": "data.New"},
                            },
                            {
                                "headerName": "OS",
                                "field": "OS",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 225,
                                "cellClassRules": {"bg-blue-500": "data.New"},
                            },
                            {
                                "headerName": "Notes (Editable)",
                                "field": "Notes",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 150,
                                "editable": True,
                                "cellClassRules": {"bg-blue-500": "data.New"},
                            },
                            {
                                "headerName": "Internal IP",
                                "field": "Internal IP",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 150,
                                "cellClassRules": {"bg-blue-500": "data.New"},
                            },
                            {
                                "headerName": "External IP",
                                "field": "External IP",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 150,
                                "cellClassRules": {"bg-blue-500": "data.New"},
                            },
                            {
                                "headerName": "Last Seen",
                                "field": "Last Seen",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 225,
                                "sort": "desc",
                                "cellClassRules": {"bg-blue-500": "data.New"},
                            },
                        ],
                        "rowSelection": "multiple",
                        "rowData": row_data,
                    },
                    html_columns=[1],
                ).classes(f"{aggrid_theme} w-full h-full")

                # handler for change
                self.aggrid.on("cellValueChanged", self._on_cell_value_changed)

        except Exception as e:
            print(f"Error rendering grid: {e}")

    def _on_cell_value_changed(self, event):
        """
        Handles cell value changes for the aggrid

        """
        # Access the event details via event.args, which is a dictionary.
        event_data = event.args
        """
        {'value': 'test', 'newValue': 'test', 'rowIndex': 1, 'data': {'Agent ID': "<u><a href='/agent/df4adb60-1653-4fd0-821a-356f12642b53'>df4adb60-1653-4fd0-821a-356f12642b53</a></u>", 'Hostname': None, 'OS': None, 'Internal IP': None, 'Last Seen': '2025-03-18 13:22:52', 'Notes': 'test'}, 'source': 'edit', 'colId': 'Notes', 'selected': True, 'rowHeight': 28, 'rowId': '0'}
        """
        if event_data.get("colId", {}) == "Notes":
            # send API request to /agents/{agent_id}/notes
            # pull agent ID from hidden ID row (Raw Agent ID)

            clicked_agent_id = event_data.get("data").get("Raw Agent ID")

            # directly get new data from event.
            note_data = {"notes": event_data.get("newValue")}
            api_post_call(f"/agent/{clicked_agent_id}/notes", data=note_data)
            ui.notify(
                f"Updated notes for {clicked_agent_id} with: {event_data.get("newValue")}",
                position="top-right",
            )


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
                ui.tab("[BETA] Shellcode Converter")
                ui.tab("Scripts")

            # -- TAB PANELS --
            with ui.tab_panels(tabs, value="Agents").classes("w-full h-full border"):
                with ui.tab_panel("Agents").classes("h-full"):
                    a = AgentsView()
                    a.render()
                with ui.tab_panel("Binaries + Builder"):
                    a = BuildView()
                    a.render()
                with ui.tab_panel("[BETA] Shellcode Converter"):
                    a = ShellcodeBuildView()
                    a.render()
                with ui.tab_panel("Scripts"):
                    a = ScriptsView()
                    a.render()
