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
import socketio
from script.script_api import load_script
import pathlib
import importlib

socketio = socketio.AsyncClient()

# -----------------------------------------------
#   Easy Settings
# -----------------------------------------------

SHELL_SCROLL_DURATION = (
    0.25  # really just speed, how long it takes for the "scroll animation" to complete
)


# -----------------------------------------------
#   UI Helper Function
# -----------------------------------------------
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


# -----------------------------------------------
#   Agent View
# -----------------------------------------------
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

    async def render(self):
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
                    await self.render_shell_tab()

            # Add a refresh button
            # ui.button("Refresh", on_click=self.refresh).classes("mt-4")

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

    async def render_shell_tab(self):
        shell = Shell(self.agent_id)
        await shell.render()
        # maybe make the shell its own class


# -----------------------------------------------
# Shell Class
# -----------------------------------------------
# lots of async here, better safe than sorry to have it for future things
class Shell:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.display_log = None
        self.command_input = None
        self.command_history = (
            []
        )  # Store previous commands to allow for history navigation

        self.send_button = None
        self.latency_text = None
        self.data_bar = None
        self.current_settings = app.storage.user.get("settings", {})
        self.last_checkin_time = 0
        self.loaded_script_module = None

    # ----------------------
    # Socket Ops
    # ----------------------
    async def register_socket_handlers(self):
        """
        Registers websockets to their correct functions

        In future iterations, with scripts, there will be overrides for the script functions to get called isntead
        of the ones linked here.
        """
        # register socket things for class
        Config.socketio.on("local_notif", self.socket_local_notif, namespace="/shell")
        await self._update_log(f"[SYSTEM] local_notif registered successfully")

        Config.socketio.on(
            "display_on_terminal", self.socket_local_notif, namespace="/shell"
        )
        await self._update_log(f"[SYSTEM] display_on_terminal registered successfully")

        Config.socketio.on(
            "on_agent_connect", self.socket_on_agent_connect, namespace="/shell"
        )
        await self._update_log(f"[SYSTEM] on_agent_connect registered successfully")

        Config.socketio.on(
            "on_agent_first_connect",
            self.socket_on_agent_first_connect,
            namespace="/shell",
        )
        await self._update_log(
            f"[SYSTEM] on_agent_first_connect registered successfully"
        )

        Config.socketio.on(
            "on_agent_data", self.socket_on_agent_data, namespace="/shell"
        )
        await self._update_log(f"[SYSTEM] on_agent_data registered successfully")

    async def connect_to_agent_room(self):
        await self._update_log(
            f"[SYSTEM] Attempting to connect to {self.agent_id} room..."
        )
        agent_data = {"agent_id": self.agent_id}
        await Config.socketio.emit("join", agent_data, namespace="/shell")

    async def socket_global_notif(self, data):
        # print("Data from soket:", data)
        await self._update_log(f"[GLOBAL_NOTIF] {data}")

    async def socket_local_notif(self, data):
        # print("Data from soket:", data)
        await self._update_log(f"[LOCAL_NOTIF] {data}")

    async def socket_set_agent_response(self, data):
        # print("Data from soket:", data)
        await self._update_log(f"[04/02 19:22:48] >> received output:\n{data}")

    # setup additional sockets
    async def socket_on_agent_connect(self, data):
        # print("Data from soket:", data)
        # await self._update_log(f"debug: agent {data} connected")
        # something like this would be good in the script, once this base is implemented
        # idea: if script.method_for_this, then script.call_method_for_it
        await self._update_log(f"[SYSTEM]: Agent checked in.")
        # on checkin, reset last checkin to 0 seconds
        await self.reset_last_checkin()

        """
        Idea here... do a check, IF related module exists in imported script...
        run that classes .run
        
        Would need special handling for custom commands
        """

        # from data.scripts.example_script import on_agent_connect

        # check if class is in script
        on_agent_connect = getattr(self.loaded_script_module, "on_agent_connect", None)
        if on_agent_connect is None:
            print("Warning: 'on_agent_connect' attribute not found in module.")
        else:
            try:
                await on_agent_connect.run(data)
            except Exception as e:
                print(f"Error running on_agent_connect.run(): {e}")

    async def socket_on_agent_first_connect(self, data):
        # print("Data from soket:", data)
        await self._update_log(f"[SYSTEM]: socket_on_agent_first_connect")
        on_agent_first_connect = getattr(
            self.loaded_script_module, "on_agent_first_connect", None
        )
        if on_agent_first_connect is None:
            print("Warning: 'on_agent_first_connect' attribute not found in module.")
        else:
            try:
                await on_agent_first_connect.run(data)
            except Exception as e:
                print(f"Error running on_agent_first_connect.run(): {e}")

    async def socket_on_agent_data(self, data):
        """
        Functino to do stuff based on when agent posts its data back

        data: str: The data from the agent

        """
        await self._update_log(data)

        on_agent_data = getattr(self.loaded_script_module, "on_agent_data", None)
        if on_agent_data is None:
            print("Warning: 'on_agent_data' attribute not found in module.")
        else:
            try:
                await on_agent_data.run(data)
            except Exception as e:
                print(f"Error running on_agent_data.run(): {e}")

    # ----------------------
    # Render
    # ----------------------

    async def render(self):
        # with ui.element().classes("m-0 p-0 w-full"):
        # render FIRST
        self._render_log()  # Ensure display_log is ready

        self.data_bar = ui.row().classes(
            "w-full h-[12px] text-grey m-0 p-0 items-center"
        )
        with self.data_bar:
            # self.latency_text = ui.label("Metadata bar: ")

            # latency
            self.latency_text = ui.label("1234")
            with self.latency_text:
                ui.tooltip("Latency between Shell & Server")

            # last checkin
            self.last_checkin_text = ui.label(0)
            with self.last_checkin_text:
                ui.tooltip("How long since the agent last checked in")

            # int_ip
            self.int_ip = ui.label("int_ip: 127.0.0.1")
            with self.int_ip:
                ui.tooltip("The internal IP of the agent")

            # ext_ip
            self.ext_ip = ui.label("ext_ip: 69.69.69.69")
            with self.ext_ip:
                ui.tooltip("The external ip of the agent")

            # ext_ip
            self.current_user = ui.label("context/user: SomeDomain\SomeUser")
            with self.current_user:
                ui.tooltip(
                    "The current user that the agent is impersonating/running under"
                )

        with ui.element().classes("flex w-full gap-2"):
            self._render_command_input()
            self._render_send_button()
            with ui.column().classes("items-center justify-center"):
                self._render_toolbox_button()

        if Config.socketio.connected:
            await self._update_log("[SYSTEM] Socket connected...")
            # register socket hanlders...
            await self.register_socket_handlers()
            # And connect to agent room after ensuring connection is established.
            await self.connect_to_agent_room()
            ui.timer(1, self.measure_latency)
            ui.timer(1, self.check_last_checkin)

        else:
            ui.notify("Socket not connected", position="top-right", type="warning")
            await self._update_log("[SYSTEM] Socket not connected...")

        # temporarily load script here
        await self._load_script("example_script")

        with ui.context_menu():
            ui.menu_item("Change Script", on_click=self.render_scripts_dialog)
            ui.menu_item("Option 2")
            ui.separator()
            with ui.menu_item("Option 3", auto_close=False):
                with ui.item_section().props("side"):
                    ui.icon("keyboard_arrow_right")
                with ui.menu().props('anchor="top end" self="top start" auto-close'):
                    ui.menu_item("Sub-option 1")
                    ui.menu_item("Sub-option 2")
                    ui.menu_item("Sub-option 3")

    def _render_log(self):
        """Create the log display area."""
        self.display_log = ui.log(max_lines=100).classes(
            "w-full h-full monospace-font "
        )

    def _render_command_input(self):
        """Create the input field for the user to type commands."""
        self.command_input = (
            ui.input(placeholder="Type a command...")
            .props('autofocus outlined input-class="ml-3" input-class="h-12"')
            .classes("text-black w-full flex-1")
            .on("keydown", self.handle_keydown)  # Listening for the keydown event
        )

    def _render_send_button(self):
        """Create the send button to process the input."""
        self.send_button = ui.button("Send", on_click=self.handle_send).classes(
            "flex-none bg-red"
        )

        with self.send_button:
            ui.tooltip("The scary button").classes("bg-red")

        # if self.current_settings.get("Client: Disarm/ReadOnly", False):
        #     with self.send_button.props("disable").classes("bg-grey"):
        #         ui.tooltip("Button disabled - Read Only Mode").classes("bg-red")

        # else:
        #     with self.send_button:
        #         ui.tooltip("The scary button").classes("bg-red")

    def _render_toolbox_button(self):
        """
        Toolbox button
        """
        # fullscreen = ui.fullscreen()
        with ui.row().classes(""):
            result = ui.label().classes("mr-auto")
            with ui.button(icon="menu"):
                ui.tooltip("More Buttons").classes("bg-green")
                with ui.menu() as menu:
                    self.render_scripts_options()
                    ui.button(
                        ">broken< Toggle Fullscreen", on_click="fullscreen.toggle"
                    ).classes("h-16")
                    ui.button(
                        "Chnage Script", on_click=self.render_scripts_dialog
                    ).classes("h-16")

                    # # ui.button('response inspector', on_click=fullscreen.toggle) # pops all json commands in the json editor
                    # ui.separator()
                    # ui.menu_item("Close", menu.close)

    # old menu
    # def render_scripts_options(self):
    #     """
    #     Renders the script options dropdown.

    #     Retrieves available scripts from the /scripts/files endpoint and the agent's current script,
    #     then creates a dropdown. Changing the selection triggers _register_script.
    #     """
    #     response = api_call(url="/scripts/files")
    #     scripts_data = (
    #         [
    #             script.get("filename", "Unknown Script")
    #             for script in response.get("data", [])
    #         ]
    #         if response.get("data")
    #         else ["No Scripts Available"]
    #     )
    #     agent_data = api_call(url=f"/stats/agent/{self.agent_id}").get("data", {})
    #     agent_info = next(iter(agent_data.values()), {})
    #     agent_script = (
    #         agent_info.get("data", {}).get("config", {}).get("command_script")
    #     )
    #     ui.select(
    #         options=scripts_data,
    #         label="Extension Scripts",
    #         on_change=lambda e: self._register_script(e.value),
    #         value=agent_script,
    #     ).classes("w-full")

    def render_scripts_options(self):
        """
        Renders the script options dropdown.

        Retrieves available scripts from the /scripts/files endpoint and the agent's current script,
        then creates a dropdown. Changing the selection triggers _register_script.
        """
        # response = api_call(url="/scripts/files")
        # scripts_data = (
        #     [
        #         script.get("filename", "Unknown Script")
        #         for script in response.get("data", [])
        #     ]
        #     if response.get("data")
        #     else ["No Scripts Available"]
        # )
        # agent_data = api_call(url=f"/stats/agent/{self.agent_id}").get("data", {})
        # agent_info = next(iter(agent_data.values()), {})
        # agent_script = (
        #     agent_info.get("data", {}).get("config", {}).get("command_script")
        # )

        scripts_dir_cwd = pathlib.Path.cwd() / "data" / "scripts"
        scripts_dir = pathlib.Path(scripts_dir_cwd)

        # Iterate over directory contents and convert each PosixPath to a string
        scripts_in_script_dir = [str(p) for p in scripts_dir.iterdir()]

        # get list of files in folder
        # format into list
        ui.select(
            options=scripts_in_script_dir,
            label="Extension Scripts",
            on_change=lambda e: self._load_script(e.value),
            # moved to load script instead of register script
        ).classes("w-full")

    def render_scripts_dialog(self):
        """Displays a help dialog for the agents tab."""
        with ui.dialog().classes() as dialog, ui.card():
            ui.markdown("# Select a script:")
            self.render_scripts_options()
            with ui.row():
                ui.button("Apply")  # onlick apply script
                ui.button("close")  # onclick close
        dialog.open()

    # ----------------------
    # Events
    # ----------------------
    async def update_latency_text(self, data):
        self.latency_text.set_text(f"Latency: {data:.2f} ms")

    async def handle_keydown(self, e):
        if e.args.get("key") == "Enter":
            await self.handle_send()

    async def handle_send(self):
        """Handle the logic for sending a command."""
        command = self.command_input.value.strip()
        if command == "clear":
            self.display_log.clear()
        if command:
            self.command_history.append(command)
            await self._process_command(command)
            self.command_input.value = ""

    async def _register_script(self, script_name):
        """
        Sends a POST request to update the agent's command script.

        Args:
            script_name (str): The new command script name.
        """
        api_post_call(
            url=f"/agent/{self.agent_id}/command-script/register",
            data={"command_script": script_name},
        )
        await self._update_log(f"[SYSTEM] Updated script to {script_name}")
        ui.notify(f"Updated script to {script_name} on agent", position="top-right")

    async def _process_command(self, command):
        """Process the command and update the log with response."""
        api_post_call(
            url=f"/agent/{self.agent_id}/command/enqueue",
            data={"command": command},
        )
        # This is where you could easily extend the system by adding more commands.
        await self._update_log(f"[04/02 19:22:14] >> Tasked agent to run: {command}")
        # await self._update_log(f"Response: SOMERESPONSE")

    async def _update_log(self, data, sender=""):
        """Update the log with the message."""

        self.display_log.push(f"{data}")

    async def measure_latency(self):
        # Record the time before sending the ping
        start_time = time.time()
        # Use sio.call to send the ping and wait for the pong response
        response = await Config.socketio.call(
            "ping", {"time": start_time}, namespace="/shell"
        )
        end_time = time.time()
        latency = (end_time - start_time) * 1000  # in milliseconds
        # ui.notify(f"Round-trip latency: {latency:.2f} ms")
        await self.update_latency_text(latency)

    async def check_last_checkin(self):
        # Record the time before sending the ping
        self.last_checkin_time = self.last_checkin_time + 1
        await self.update_last_checkin_text(self.last_checkin_time)

    async def reset_last_checkin(self):
        self.last_checkin_time = 0

    async def update_last_checkin_text(self, data):
        self.last_checkin_text.set_text(f"Last Checkin: {data:.2f} s ago")

    # ----------------------
    # Misc
    # ----------------------
    async def _load_script(self, script="example_script"):
        """
        Function called to load a script from the GUI. Loads a script into
        the current shell/agent session


        script (str): The script to be loaded into the current agent session
        """

        try:
            # await load_script(script)
            path = pathlib.Path.cwd() / "data" / "scripts" / f"{script}.py"

            if not path.exists():
                print(f"Script file not found: {path}")
                return

            # Create a spec from the file location.
            spec = importlib.util.spec_from_file_location(script, str(path))
            if spec is None:
                print("Could not load spec for", str(path))
                return
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # set the self.module so it can be used elsewehre
            self.loaded_script_module = module

            msg = f"[SYSTEM] Script successfully loaded: {script}"
            await self._update_log(data=msg)

        except Exception as e:
            msg = f"[ERROR] Could not load script {script}: {e}"
            await self._update_log(data=msg)
            print(msg)


# -----------------------------------------------
#   Agents List View
# -----------------------------------------------
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

        ui.timer(5, self.update_aggrid_times)

    async def update_aggrid_times(self):
        self.aggrid.options["rowData"][0]["Last Seen"] = "HI THERE"
        self.aggrid.update()


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
