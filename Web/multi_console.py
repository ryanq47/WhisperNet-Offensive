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
from agent import AgentsView, AgentView


class MultiConsolePage:
    """
    Multi console for interacting with multiple agents
    """

    def __init__(self, agent_id: str = None):
        self.list_of_agent_ids = (
            []
        )  # A list to track which agents have been queued commands based on what is selected
        self.list_of_command_ids = (
            []
        )  # anda list to track the queued commands based on ID

    async def open_help_dialog(self) -> None:
        """Open a help dialog with instructions for the shellcode converter."""
        with ui.dialog().classes("w-full").props("full-width") as dialog, ui.card():
            ui.markdown("# *the* MultiConsole:")
            ui.separator()
            ui.markdown(
                """
                One of whispernet's more powerful features, is the 

                *MULTICONSOLE*

                It allows you to send commands to whatever selection of clients you want.

                Plus scripts are supported, so if you wanted to be a menace and run goose desktop
                on every machine you have, you can!

                """
            )
            ui.separator()
            ui.markdown(
                """
                #### Usage:
                        
                1. Select the clients you want from the left side menu
                2. Choose a script (clients need to be selected first, otherwise the script will not apply to them)
                3. Start sending commands!

                Each command has the agent UUID on it, so you can tell which response goes to which client.
                Ex: `[734e1623-7ce3-4c67-80a6-93a1a8ef367f] > shell whoami`
                        """
            )
        dialog.open()
        await dialog

    def render_help_button(self) -> None:
        """Render a help button pinned at the bottom-right of the screen."""
        help_button = ui.button("Current Page Info", on_click=self.open_help_dialog)
        help_button.style("position: fixed; top: 120px; right: 24px; ")

    def render(self):
        """
        Renders the complete agent view including header, tabs, and tab panels.
        """
        self.render_help_button()
        with ui.column().classes("w-full h-full"):
            with ui.row().classes("w-full text-5xl"):
                ui.icon("computer")
                ui.label("MultiConsole").classes("h-10")

            ui.separator()

            with ui.splitter().classes("h-full w-full") as splitter:
                with splitter.before:
                    # maybe get a custom one in here with a select option?
                    self.mutliconsoleagentsview = MultiConsoleAgentsView()
                    self.mutliconsoleagentsview.render()
                    # ui.label("Agents Aggrid")
                with splitter.after:
                    # custom console here too
                    self.render_shell()

    def render_shell(self):
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

        # kind of messy. But in a nutshell, tracks ONLY enqueud commands, and maps them back on screen.
        def update_shell_data():
            responses_from_agents = []
            for queued_command_id in self.list_of_command_ids:
                data = api_call(url=f"/agent/command/{queued_command_id}").get(
                    "data", []
                )
                # If data is a list and its first element is a dict, then assume it's full command objects.
                if data and isinstance(data, list):
                    if isinstance(data[0], dict):
                        responses_from_agents.extend(data)
                    # otherwise, it's a list of ID's, so do a lookup for each
                    elif isinstance(data[0], str):
                        # data is a list of command IDs; perform an additional lookup for each one.
                        for cmd_id in data:
                            full_command = api_call(url=f"/agent/command/{cmd_id}").get(
                                "data", {}
                            )
                            if full_command and isinstance(full_command, dict):
                                responses_from_agents.append(full_command)
                elif isinstance(data, dict):
                    responses_from_agents.append(data)

            # Sort entries chronologically.
            responses_from_agents.sort(key=lambda entry: entry.get("timestamp", ""))
            for entry in responses_from_agents:
                # Use a unique identifier for the command.
                cmd_id = entry.get("command_id", "")
                if not cmd_id:
                    cmd_id = f"no_id_{entry.get('timestamp', '')}"
                cmd = entry.get("command", "")
                agent_id = entry.get("agent_id", "")
                response_value = entry.get("response") or "Waiting on callback..."

                if cmd_id not in self.known_command_ids:
                    # Append new entry HTML to the output element.
                    html = (
                        f"<div id='shell_entry_{cmd_id}' style='margin-bottom: 10px;'>"
                        f"<div style='font-family: monospace;'>[{agent_id}] &gt; {cmd}</div>"
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

        async def send_command():
            # api_post_call(
            #     url=f"/agent/{self.agent_id}/command/enqueue",
            #     data={"command": command_input.value},
            # )

            self.list_of_agent_ids = (
                await self.mutliconsoleagentsview.get_selected_agents()
            )

            for agent_id in self.list_of_agent_ids:
                # ui.notify(f"{agent_id}", position="top-right")

                """
                Okkkayyy... discussion time. Can either create a multiqueue endpoint (may be best for API purposes/best practices)
                or just loop over each selected agent and send to the enqueue URL. < faster to implement,  and easier.

                """
                request_output = api_post_call(
                    url=f"/agent/{agent_id}/command/enqueue",
                    data={"command": command_input.value},
                )

                extracted_command_id = request_output.get("data", "")
                if isinstance(extracted_command_id, list):  # if list/list of ID's
                    self.list_of_command_ids.extend(extracted_command_id)
                else:
                    self.list_of_command_ids.append(extracted_command_id)

                # gonna need to check each agent id as well for responses to this message. Switch from one id to a loop
                """
                    Plan here: Have a get one command endpoint for an agent - or just a general command id lookup endpoint, no agent id needed
                    For each command id, fetch the command results as usual

                    /stats/agents/command
                
                """
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
        # agent_data = api_call(url=f"/stats/agent/{self.agent_id}").get("data", {})

        # # Get the inner dictionary, which holds the actual agent info. Only one agent is returned from this call, so it'll just grab the first one
        # agent_info = next(iter(agent_data.values()), {})

        # # Then navigate to the command_script inside the nested structure.
        # agent_script = (
        #     agent_info.get("data", {}).get("config", {}).get("command_script")
        # )

        # Create the script selector dropdown.
        ui.select(
            options=scripts_data,
            label="Extension Scripts",
            on_change=lambda e: self._register_script(e.value),
        ).classes("w-full ")

    async def _register_script(self, script_name):
        """
        POST call to update the script for an agent on the server

        script_name: The name of the script on the server

        Usually this would be under the render_scripts_options method, but ui.select needs a callback func to call on change

        Endpoint: /agent/{self.agent_id}/command-script/register

        """
        self.list_of_agent_ids = await self.mutliconsoleagentsview.get_selected_agents()
        # need to get selected agents
        for agent_id in self.list_of_agent_ids:
            api_post_call(
                url=f"/agent/{agent_id}/command-script/register",
                data={"command_script": script_name},
            )
            ui.notify(f"Updated script to {script_name} on agent", position="top-right")


# ---------------------------
#   Agents List View
#   Use a slightly modified agents view for the multi console, that include select + handling
# ---------------------------
class MultiConsoleAgentsView:
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

            # on change handler
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

    async def get_selected_agents(self):
        rows = await self.aggrid.get_selected_rows()
        list_of_agents = []
        if rows:
            for row in rows:
                agent_id = row.get("Raw Agent ID", "")
                # ui.notify(f"{agent_id}", position="top-right")
                # url = f"{Config.API_HOST}/build/{filename}"
                # ui.download(url)
                # trigger refresh
                # self.on_refresh()
                list_of_agents.append(agent_id)
            return list_of_agents
        else:
            ui.notify("No agents selected.", position="top-right")
            return None
