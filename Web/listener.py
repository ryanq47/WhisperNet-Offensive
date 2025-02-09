from nicegui import ui, app
import requests
from config import Config, ThemeConfig
from networking import api_call, api_post_call, api_delete_call


class ListenerView:
    def __init__(self, listener_id=None):
        self.listener_id = str(listener_id)

        self.request_data = api_call(url=f"/stats/listener/{self.listener_id}")

        data = self.request_data.get("data", {})
        first_key = next(iter(data))  # Get the first key dynamically
        self.listener_data = data.get(first_key, {})

    # ------------------------------------------------------------------------
    #                      Render
    # ------------------------------------------------------------------------

    def render(self):
        with ui.element().classes("w-full h-full"):

            current_settings = app.storage.user.get("settings", {})

            with ui.tabs() as tabs:
                ui.tab("MAIN")
                # ui.tab('OTHER')
                if current_settings.get("Dev Mode", False):
                    ui.tab(
                        "STATS"
                    )  # Graphs N Stuff? There's examples of this in nicegui examples
                    # ui.tab('FileExplorer')
                    ui.tab("NOTES")
            with ui.tab_panels(tabs, value="MAIN").classes("w-full h-full border"):
                with ui.tab_panel("MAIN"):
                    # ui.label('Content of A')
                    self.render_main_tab()

                if current_settings.get("Dev Mode", False):
                    with ui.tab_panel("STATS"):
                        # ui.label('Content of A')
                        self.render_stats_tab()
                    with ui.tab_panel("NOTES"):
                        # ui.label('Content of A')
                        self.render_notes_tab()

    # ------------------------------------------------------------------------
    #                      Main Tab
    # ------------------------------------------------------------------------
    def render_main_tab(self):
        current_settings = app.storage.user.get("settings", {})

        # with ui.header().classes(replace='row items-center').classes('bg-neutral-800') as header:
        # ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
        with ui.row().classes("text-5xl"):
            ui.icon("computer")
            ui.label("ListenerName").classes("h-10  600")
        # reduce space here
        with ui.row().classes("w-full text-2xl"):
            ui.icon("badge")
            ui.label(self.listener_id).classes("h-6  400")
            ui.space()
            # ui.icon("timer")
            # ui.label("Last Checkin: 01:01:01 ").classes("h-6  400")
        ui.separator()

        with ui.row().classes("w-full h-full flex"):
            # Details Section
            with ui.column().classes("flex-1 h-full"):
                with ui.row().classes("items-center justify-between w-full"):
                    ui.label("Details").classes("h-6  400")
                ui.separator()
                create_ui_from_json(self.listener_data)

                # create_ui_from_json(self.agent_data)

            # Command History Section
            with ui.column().classes("flex-1 h-full"):
                aggrid_theme = (
                    "ag-theme-balham-dark"
                    if current_settings.get("Dark Mode", False)
                    else "ag-theme-balham"
                )
                # Header for Command History
                ui.label("Connected Clients").classes("h-6  400")
                ui.separator()

                mydict = []
                for i in range(1, 100):
                    mydict.append(
                        {
                            "ID": "1234-1234-1234-1234",
                            "name": "agent_01",
                            "open": "somebutton",
                        }
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
                                    "headerName": "ID",
                                    "field": "id",
                                    "filter": "agTextColumnFilter",
                                    "floatingFilter": True,
                                },
                                {
                                    "headerName": "Name",
                                    "field": "name",
                                    "filter": "agTextColumnFilter",
                                    "floatingFilter": True,
                                },
                                {
                                    "headerName": "Open",
                                    "field": "open",
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

                # Full-width Button: Below Agents section
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

                ui.label("Test Graph - Connected clients").classes("h-6  400")
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

    # ------------------------------------------------------------------------
    #                      Notes Tab
    # ------------------------------------------------------------------------

    def render_notes_tab(self):
        ...
        # with ui.row().classes('w-full h-full flex'):
        #     # Move to somethign server based, or find a better way to save these session wise?
        #     ui.textarea('User notes. NOTE! These are stored in the current session, aka only YOU can see these, in this browser. THEY WILL DISAPPEAR ON DIFFERENT BROWSERS - Fix This to have a notes endpoint for agents + save, etc').classes('w-full').bind_value(app.storage.user, 'note')


class ListenersView:
    """
    A list of listeners
    """

    def __init__(self):

        self.request_data = api_call(url=f"/stats/listeners")

        # get top level data key from response
        self.request_data = self.request_data.get("data", {})

    def render(self):
        ui.button(
            text="Spawn Listener",
            on_click=lambda: self.render_spawn_listener_dialogue(),
        ).classes("w-full")
        self.render_listeners_grid()

    def render_listeners_grid(self):
        current_settings = app.storage.user.get("settings", {})

        try:
            # NOTES:
            #     Adapting for listeners.
            #     Similar setup to agents, adjusted for listener data fields.

            # Extract the relevant data
            listeners = self.request_data  # Assuming this is where your data resides
            row_data = []
            for key, listener_info in listeners.items():
                listener_id = listener_info.get("listener_id", "Unknown")
                name = listener_info.get("name", "Unknown")
                address = (
                    listener_info.get("data", {})
                    .get("network", {})
                    .get("address", "Unknown")
                )
                port = (
                    listener_info.get("data", {})
                    .get("network", {})
                    .get("port", "Unknown")
                )
                protocol = (
                    listener_info.get("data", {})
                    .get("network", {})
                    .get("protocol", "Unknown")
                )

                # Append formatted row
                row_data.append(
                    {
                        "Listener ID": f"<u><a href='/listener/{listener_id}'>{listener_id}</a></u>",
                        "Name": name,
                        "Address": address,
                        "Port": port,
                        "Protocol": protocol,
                    }
                )

            # Render the aggrid
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
                                "headerName": "Listener ID",
                                "field": "Listener ID",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 225,
                            },
                            {
                                "headerName": "Name",
                                "field": "Name",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 225,
                            },
                            {
                                "headerName": "Address",
                                "field": "Address",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 225,
                            },
                            {
                                "headerName": "Port",
                                "field": "Port",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 100,
                            },
                            {
                                "headerName": "Status (Alive/Dead/Unresponsive, etc)",
                                "field": "Status",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 100,
                            },
                            {
                                "headerName": "Protocol (HTTP, HTTPS, DNS, etc)",
                                "field": "Protocol",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 100,
                            },
                        ],
                        "rowData": row_data,
                    },
                    html_columns=[0],
                ).classes(f"{aggrid_theme} w-full h-full")
        except Exception as e:
            print(f"Error rendering grid: {e}")

    async def render_spawn_listener_dialogue(self):
        """
        Opens a dialog for spawning a new listener.
        When the user submits, the dialog closes and spawn_listener() is called with values from the dialog.
        """
        # Create the dialog and its contents
        with ui.dialog() as dialog, ui.card():
            ui.label("Spawn a New Listener")
            # Input fields for the dialog
            with ui.element().classes(
                "w-full"
            ):  # make sure fields are full width of parent dialogue container
                name_input = ui.input(label="Listener Name")
                protocol_input = ui.input(label="Listener Type [dropdown me later]")
                address_input = ui.input(label="Listener Address")
                port_input = ui.input(label="Listener Port")

            with ui.row():
                # When "Submit" is clicked, the dialog is closed and returns a dict of values. kinda weird
                ui.button(
                    "Start Listener",
                    on_click=lambda: dialog.submit(
                        {
                            "name": name_input.value,
                            "port": port_input.value,
                            "protocol": protocol_input.value,
                            "address": address_input.value,
                        }
                    ),
                )
                # When "Cancel" is clicked, simply close the dialog returning None
                ui.button("Cancel", on_click=lambda: dialog.submit(None))

        dialog.open()  # Display the dialog

        # Wait for the dialog to close and capture the result
        result = await dialog
        if result is not None:
            # Call a different function (e.g., spawn_listener) with the collected values
            self.spawn_listener(
                result.get("name", ""),
                result.get("port", ""),
                result.get("protocol", ""),
                result.get("address", ""),
            )
        else:
            ui.notify("Listener creation was canceled.")

    # Example function to be called with the dialog values
    def spawn_listener(self, name: str, port: str, protocol: str, address: str):
        print(
            f"Spawning {protocol} listener with name: {name} @ {address} on port: {port}"
        )
        # network call + stuff

        listener_dict = {"port": port, "host": address, "name": name}

        # will need to move to a universal listener spawner, or have a per protocol call here.
        # first sounds better, but is harder/takes longer, 2nd is the easy fix.

        api_post_call(data=listener_dict, url="/listener/http/spawn")


# page itself
class ListenersPage:
    def __init__(self): ...

    def render(self):
        with ui.column().classes("w-full h-full p-[10px]"):
            # HEADER 1
            with ui.row().classes("w-full text-5xl"):
                ui.icon("computer")
                ui.label("Listeners").classes("h-10")

            # HEADER 2
            with ui.row().classes("w-full text-2xl"):
                ui.icon("construction")
                ui.label("Monitor, Access, and Spawn Listeners").classes("h-6")
                ui.space()
            ui.separator()

            # -- TABS --
            with ui.tabs() as tabs:
                ui.tab("Listeners")

            # -- TAB PANELS --
            with ui.tab_panels(tabs, value="Listeners").classes("w-full h-full border"):
                with ui.tab_panel("Listeners"):
                    a = ListenersView()
                    a.render()


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
