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
from perf_testing import *

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

    This class handles:
      - Loading agent details from the /stats/agent/{agent_id} endpoint.
      - Checking and updating the agent "new" status.
      - Rendering a multi-tab view with the agent's main details and shell command history.
      - Providing a refresh mechanism to update the displayed data.
    """

    def __init__(self, agent_id: str = None):
        self.agent_id = str(agent_id)
        self.agent_data = {}  # To be populated via load_data()
        self.command_grid = None  # Reference to the AG Grid for commands
        self.known_command_ids = {}  # Tracks rendered shell entries
        self.auto_scroll_enabled = True

    def load_data(self):
        """
        Loads agent data synchronously from the /stats/agent/{agent_id} endpoint.

        Processes the response and stores the relevant data in self.agent_data.
        Also checks and updates the 'new' status of the agent.
        """
        response = api_call(url=f"/stats/agent/{self.agent_id}")
        data = response.get("data", {})
        if data:
            first_key = next(iter(data))
            self.agent_data = data.get(first_key, {})
        else:
            self.agent_data = {}
        self.check_new_status()

    def check_new_status(self):
        """
        Checks if the agent is marked as 'new' and, if so, sends a POST request to update its status.
        Notifies the user that the agent is no longer considered new.
        """
        if self.agent_data.get("data", {}).get("agent", {}).get("new"):
            ui.notify(
                "Agent clicked into, no longer considered new", position="top-right"
            )
            data = {"new": False}
            api_post_call(f"/agent/{self.agent_id}/new", data=data)

    def refresh(self):
        """
        Refreshes the agent view by reloading data and re-rendering the view.
        """
        self.load_data()
        self.render()  # For a complete re-render; alternatively, update specific UI parts

    # --------------------
    # Rendering Funcs
    # --------------------

    def render(self):
        """
        Renders the complete agent view including header, tabs, and tab panels.

        Calls load_data() to ensure that the latest data is available before rendering.
        """
        # Load or refresh data first
        self.load_data()
        with ui.element().classes("w-full h-full"):
            current_settings = app.storage.user.get("settings", {})

            # Create tabs for MAIN and SHELL views
            with ui.tabs() as tabs:
                ui.tab("MAIN")
                ui.tab("SHELL")

            # Render the content for each tab
            with ui.tab_panels(tabs, value="MAIN").classes("w-full h-full border"):
                with ui.tab_panel("MAIN").classes("h-full"):
                    self.render_main_tab()
                with ui.tab_panel("SHELL").classes("h-full"):
                    self.render_shell_tab()

            # Add a refresh button
            ui.button("Refresh", on_click=self.refresh).classes("mt-4")

    def render_main_tab(self):
        """
        Renders the MAIN tab containing the agent details and the command history grid.
        """
        hostname = (
            self.agent_data.get("data", {})
            .get("system", {})
            .get("hostname", "Unknown Hostname")
        )
        last_seen = (
            self.agent_data.get("data", {}).get("agent", {}).get("last_seen", "Unknown")
        )

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

        with ui.row().classes("w-full h-full flex"):
            # Left side: Display agent details
            with ui.column().classes("flex-1 h-full"):
                with ui.row().classes("items-center justify-between w-full"):
                    ui.label("Details").classes("h-6")
                ui.separator()
                with ui.scroll_area().classes("h-full"):
                    create_ui_from_json(self.agent_data)
            # Right side: Command history grid
            with ui.column().classes("flex-1 h-full"):
                aggrid_theme = (
                    "ag-theme-balham-dark"
                    if app.storage.user.get("settings", {}).get("Dark Mode", False)
                    else "ag-theme-balham"
                )
                ui.label("Command History").classes("h-6")
                ui.separator()
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

    def render_shell_tab(self):
        shell = Shell(self.agent_id)
        shell.render()
        # maybe make the shell its own class

    # def render_shell_tab(self):
    #     """
    #     Renders the SHELL tab with a scrollable command history and an input area.

    #     Auto-refresh is set up to update the shell output every second.
    #     """
    #     self.auto_scroll_enabled = True
    #     self.known_command_ids = {}
    #     self.render_scripts_options()  # Render the dropdown for script selection

    #     async def handle_keydown(e):
    #         if e.args.get("key") == "Enter":
    #             await send_command()

    #     def on_scroll(e):
    #         self.auto_scroll_enabled = e.vertical_percentage >= 0.95

    #     shell_container = ui.column()

    #     # Dictionary to keep track of pending commands: {command_uuid: label_widget}
    #     pending_commands = {}

    #     def update_shell_data():
    #         data = api_call(url=f"/agent/{self.agent_id}/command/latest").get(
    #             "data", []
    #         )
    #         if not data:
    #             return

    #         ui.notify(data)

    #         # data.sort(key=lambda entry: entry.get("timestamp", ""))
    #         for command in data:
    #             uuid = command.get("uuid")
    #             response = command.get("response", "")

    #             # If this is a new command that hasn't been displayed yet:
    #             if uuid not in pending_commands:
    #                 if response:
    #                     # If there's already a response, display it directly
    #                     with shell_container:
    #                         ui.label(
    #                             response,
    #                         )  # style="user-select: text;")
    #                 else:
    #                     # Display a placeholder and add it to pending_commands
    #                     with shell_container:
    #                         label = ui.label(
    #                             "waiting on command",
    #                             # style="user-select: text;",
    #                         )
    #                         pending_commands[uuid] = label
    #             else:
    #                 # If this command was pending, check if the response is now available
    #                 if response and pending_commands[uuid].text == "waiting on command":
    #                     # Update the label text with the new response
    #                     pending_commands[uuid].text = response
    #                     # Optionally, remove it from pending_commands if you no longer need to update it
    #                     del pending_commands[uuid]

    #     # You can then use a timer to poll this function every few seconds:
    #     ui.timer(interval=5, callback=update_shell_data)

    #     def send_command():
    #         api_post_call(
    #             url=f"/agent/{self.agent_id}/command/enqueue",
    #             data={"command": command_input.value},
    #         )
    #         command_input.value = ""
    #         update_shell_data()

    #     with ui.column().classes("h-full w-full flex flex-col"):
    #         with ui.row().classes("grow w-full p-4"):
    #             with ui.scroll_area(on_scroll=on_scroll).classes(
    #                 "w-full h-full border rounded-lg p-2"
    #             ):
    #                 ui.html(
    #                     "<div id='shell_output' style='white-space: pre-wrap; font-family: monospace;'>Shell Output:</div>"
    #                 )
    #         with ui.row().classes("w-full items-center p-4"):
    #             command_input = (
    #                 ui.textarea(placeholder="Type a command...")
    #                 .props('autofocus outlined input-class="ml-3" input-class="h-12"')
    #                 .classes("text-black grow mr-4")
    #                 .on("keydown", handle_keydown)
    #             )
    #             ui.button("Send Command", on_click=send_command).classes("w-32")
    #     update_shell_data()
    #     ui.timer(interval=1.0, callback=update_shell_data)

    # --------------------
    # Scripts funcs
    # --------------------

    def render_scripts_options(self):
        """
        Renders the script options dropdown.

        Retrieves available scripts from the /scripts/files endpoint and the agent's current script,
        then creates a dropdown. Changing the selection triggers _register_script.
        """
        response = api_call(url="/scripts/files")
        scripts_data = (
            [
                script.get("filename", "Unknown Script")
                for script in response.get("data", [])
            ]
            if response.get("data")
            else ["No Scripts Available"]
        )
        agent_data = api_call(url=f"/stats/agent/{self.agent_id}").get("data", {})
        agent_info = next(iter(agent_data.values()), {})
        agent_script = (
            agent_info.get("data", {}).get("config", {}).get("command_script")
        )
        ui.select(
            options=scripts_data,
            label="Extension Scripts",
            on_change=lambda e: self._register_script(e.value),
            value=agent_script,
        ).classes("w-full")

    def _register_script(self, script_name):
        """
        Sends a POST request to update the agent's command script.

        Args:
            script_name (str): The new command script name.
        """
        api_post_call(
            url=f"/agent/{self.agent_id}/command-script/register",
            data={"command_script": script_name},
        )
        ui.notify(f"Updated script to {script_name} on agent", position="top-right")


# class Shell:
#     def __init__(self, agent_id):
#         self.display_log = None
#         self.command_input = None

#     def render(self):
#         self.display_log = ui.log(max_lines=100).classes("w-full h-full")

#         self.render_command_input()
#         ui.button(on_click=self.update_log)

#     def render_command_input(self):
#         self.command_input = (
#             ui.textarea(placeholder="Type a command...")
#             .props('autofocus outlined input-class="ml-3" input-class="h-12"')
#             .classes("text-black grow mr-4")
#             # .on("keydown", handle_keydown)
#         )

#     def update_log(self):
#         self.display_log.push("SomeText")


class Shell:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.display_log = None
        self.command_input = None
        self.command_history = (
            []
        )  # Store previous commands to allow for history navigation

    def render(self):
        """Main render method to create the shell interface."""
        self._render_log()
        self._render_command_input()
        self._render_send_button()

    def _render_log(self):
        """Create the log display area."""
        self.display_log = ui.log(max_lines=100).classes("w-full h-full monospace-font")

    def _render_command_input(self):
        """Create the input field for the user to type commands."""
        self.command_input = (
            ui.textarea(placeholder="Type a command...")
            .props('autofocus outlined input-class="ml-3" input-class="h-12"')
            .classes("text-black grow mr-4")
            .on("keydown", self.handle_keydown)
        )

    def _render_send_button(self):
        """Create the send button to process the input."""
        ui.button("Send", on_click=self.handle_send).classes("w-1/4")

    def handle_keydown(self, event):
        """Optional: Handle keydown events like entering commands with the Enter key."""
        if event.key == "Enter":
            self.handle_send()

    def handle_send(self):
        """Handle the logic for sending a command."""
        command = self.command_input.value.strip()
        if command:
            self.command_history.append(command)
            self._update_log(f"Command: {command}")
            self._process_command(command)
            self.command_input.value = ""

    def _process_command(self, command):
        """Process the command and update the log with response."""
        # This is where you could easily extend the system by adding more commands.
        response = self._get_fake_response(command)
        self._update_log(f"Response: {response}")

    def _get_fake_response(self, command):
        """Simulate fake responses for specific commands."""
        fake_responses = {
            "whoami": output,
            "ipconfig": "IPv4: 192.168.1.100\nMask: 255.255.255.0",
            "hostname": "WIN-TEST-BOX",
            "ls": "Documents\nDownloads\nPictures\nMusic\n",
            "pwd": "/home/user1",
        }
        return fake_responses.get(command, f"Unknown command: {command}")

    def _update_log(self, message):
        """Update the log with the message."""
        self.display_log.push(f"{message} - some:time:1234")


output = """
04/01/2024  02:22 AM            40,960 wsock32.dll
03/18/2025  10:31 PM            69,632 wsplib.dll
03/18/2025  10:31 PM         1,738,184 wsp_fs.dll
03/18/2025  10:31 PM         1,512,904 wsp_health.dll
03/18/2025  10:31 PM           902,576 wsp_sr.dll
04/01/2024  02:22 AM            86,016 wsqmcons.exe
03/18/2025  10:31 PM           139,264 WSReset.exe
03/18/2025  10:31 PM           124,208 WSTPager.ax
12/14/2023  05:20 PM           230,112 WTabletSettingsAPI.dll
03/18/2025  10:31 PM            79,280 wtdccm.dll
03/18/2025  10:31 PM            54,704 wtdhost.dll
03/18/2025  10:31 PM            54,688 wtdsensor.dll
03/18/2025  10:31 PM           100,672 wtsapi32.dll
03/18/2025  10:31 PM           237,472 wuapi.dll
03/18/2025  10:31 PM            45,984 wuapihost.exe
03/18/2025  10:32 PM           152,480 wuauclt.exe
03/18/2025  10:32 PM           181,168 wuaueng.dll
03/18/2025  10:31 PM           360,448 wuceffects.dll
03/18/2025  10:31 PM            77,824 WUDFCoinstaller.dll
03/18/2025  10:31 PM           228,792 WUDFCompanionHost.exe
03/18/2025  10:31 PM           382,408 WUDFHost.exe
03/18/2025  10:31 PM           294,864 WUDFPlatform.dll
03/18/2025  10:31 PM            77,824 WudfSMCClassExt.dll
07/05/2023  09:46 AM         2,163,016 WudfUpdate_01009.dll
03/18/2025  10:31 PM           663,552 WUDFx.dll
03/18/2025  10:31 PM           836,184 WUDFx02000.dllThe system cannot write to the specified device.

"""


# ---------------------------
#   Agents List View
# ---------------------------
# Cleaned-up
class AgentsView:
    """
    Displays a list of agents with refresh and help functionality.

    This class is responsible for:
      - Fetching agent data from the API via a synchronous call.
      - Converting the fetched data into a row format suitable for AG Grid.
      - Rendering an AG Grid to display agent details such as Agent ID, Hostname, OS, Notes, IP addresses, and last check-in time.
      - Handling cell value changes (for example, when editing the "Notes" field) by sending update calls to the API.
      - Providing a help dialog and a refresh button to reload and update the displayed data.

    Attributes:
      agents_data (dict): Dictionary containing agent data fetched from the API.
      aggrid (object): The AG Grid component that displays the agents.
      current_settings (dict): User settings (such as theme) loaded from session storage.

    Methods:
      load_data():
          Fetches agent data synchronously from the '/stats/agents' endpoint and stores it in the agents_data attribute.

      refresh_data():
          Reloads the agent data by calling load_data(), rebuilds the grid row data, updates the AG Grid, and notifies the user.

      open_help_dialog():
          Opens a full-width dialog that displays help text explaining the functionality of the Agents tab.

      render_help_button():
          Renders a help button fixed in the upper-right corner; clicking it opens the help dialog.

      _on_cell_value_changed(event):
          Handles updates when an editable cell (e.g., the "Notes" field) changes.
          Extracts the new value and sends a POST request to update the corresponding agent's notes.

      render_grid():
          Renders the AG Grid component using the row data built from agents_data.
          Applies theme settings and registers the cell value change event handler.

      build_row_data():
          Processes the raw agents_data and converts it into a list of dictionaries formatted for the AG Grid.

      render():
          Main render method. Loads agent data, renders the grid, and adds a refresh button.
    """

    def __init__(self):
        self.agents_data = {}
        self.aggrid = None
        self.current_settings = app.storage.user.get("settings", {})

    # --------------------
    # Help Button
    # --------------------
    def open_help_dialog(self):
        """Displays a help dialog for the agents tab."""
        with ui.dialog().classes("w-full").props("full-width") as dialog, ui.card():
            ui.markdown("# Agents Tab:")
            ui.separator()
            ui.markdown(
                "This tab displays all connected agents. Click on an agent's UUID to view details. "
                "Use the 'Refresh Data' button below to reload the latest data."
            )
        dialog.open()

    def render_help_button(self):
        """Render a help button in the upper right corner."""
        help_button = ui.button("Current Page Info", on_click=self.open_help_dialog)
        help_button.style("position: fixed; top: 170px; right: 24px; ")

    # --------------------
    # Aggrid editable notes
    # --------------------
    def _on_cell_value_changed(self, event):
        """
        Handles updates when a cell’s value changes (for example, when editing the 'Notes' field).
        """
        event_data = event.args
        if event_data.get("colId") == "Notes":
            clicked_agent_id = event_data.get("data").get("Raw Agent ID")
            note_data = {"notes": event_data.get("newValue")}
            api_post_call(f"/agent/{clicked_agent_id}/notes", data=note_data)
            ui.notify(
                f"Updated notes for {clicked_agent_id} with: {event_data.get('newValue')}",
                position="top-right",
            )

    # --------------------
    # Aggrid
    # --------------------
    @func_call_time
    def render_grid(self):
        """Renders the AG Grid with agent data."""
        self.render_help_button()
        row_data = self.build_row_data()
        aggrid_theme = (
            "ag-theme-balham-dark"
            if self.current_settings.get("Dark Mode", False)
            else "ag-theme-balham"
        )
        with ui.column().classes("w-full h-full overflow-auto"):
            self.aggrid = ui.aggrid(
                {
                    "columnDefs": [
                        {
                            "headerName": "",
                            "checkboxSelection": True,
                            "headerCheckboxSelection": True,
                            "width": 50,
                            "pinned": "left",
                            "floatingFilter": True,
                            "cellClassRules": {"bg-blue-500": "data.New"},
                        },
                        {
                            "headerName": "Link Agent ID",
                            "field": "Link Agent ID",
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                            "width": 225,
                            "cellClassRules": {"bg-blue-500": "data.New"},
                        },
                        {
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
            self.aggrid.on("cellValueChanged", self._on_cell_value_changed)

    def build_row_data(self):
        """Builds a list of dictionaries for AG Grid from the loaded agent data."""
        row_data = []
        for key, agent_info in self.agents_data.items():
            agent_id = agent_info.get("agent_id", "Unknown")
            hostname = (
                agent_info.get("data", {}).get("system", {}).get("hostname", "Unknown")
            )
            os = agent_info.get("data", {}).get("system", {}).get("os", "Unknown")
            notes = agent_info.get("data", {}).get("agent", {}).get("notes", "")
            internal_ip = (
                agent_info.get("data", {})
                .get("network", {})
                .get("internal_ip", "Unknown")
            )
            external_ip = (
                agent_info.get("data", {})
                .get("network", {})
                .get("external_ip", "Unknown")
            )
            last_seen = (
                agent_info.get("data", {}).get("agent", {}).get("last_seen", "Unknown")
            )
            new_agent = agent_info.get("data", {}).get("agent", {}).get("new", False)

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
                    "New": new_agent,
                }
            )
        return row_data

    # --------------------
    # Class entrypoint + Important funcs
    # --------------------

    def load_data(self):
        """Load agent data synchronously.

        This way allows for easy data refresh, etc.
        """
        try:
            response = api_call(url="/stats/agents")
            self.agents_data = response.get("data", {})
        except Exception as e:
            ui.notify(f"Error loading agents: {e}", type="negative")
            self.agents_data = {}

    def refresh_data(self):
        """Refreshes everything on page"""

        # grab new data
        self.load_data()
        if self.aggrid:
            # toss new data into aggrid
            self.aggrid.options["rowData"] = self.build_row_data()
            self.aggrid.update()
            ui.notify("Data refreshed", type="positive", position="top-right")

    def render(self):
        """Main render method: load data, render grid, and add a refresh button."""

        # Load data on render. COULD swithc to async later.
        self.load_data()
        self.render_grid()
        ui.button("dev - Refresh Data", on_click=self.refresh_data).classes("mt-4")


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
