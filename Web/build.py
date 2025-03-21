from nicegui import ui, app
import requests
from config import Config
from networking import api_call, api_post_call, api_delete_call


## Filevliew


class BuildView:
    """
    Displays a page for managing files in the static-serve plugin,
    now split into two tabs: 'Files' (AG Grid) and 'Build'.
    """

    def __init__(self):
        self.file_list = []
        self.aggrid_element = None

    def fetch_file_list(self):
        resp = api_call("/build/compiled")
        self.file_list = resp.get("data", [])

    def on_refresh(self):
        self.fetch_file_list()
        self.update_aggrid()

    # handle key inputs
    # def handle_key(self, e: KeyEventArguments):
    #     # can't do due to async problems
    #     # if e.key == "Delete" and not e.action.repeat and e.action.keydown:
    #     #     ui.notify("Del key presses")
    #     #     asyncio.create_task(self.delete_selected_rows())  # Key change

    #     # if e.key == "Backspace" and not e.action.repeat and e.action.keydown:
    #     #     ui.notify("Backspace key presses")
    #     #     asyncio.create_task(self.delete_selected_rows())  # Key change

    #     if e.key == "r" and not e.action.repeat and e.action.keydown:
    #         ui.notify("Refreshing...", position="top-right")
    #         self.on_refresh()

    # if e.key == "d" and not e.action.repeat and e.action.keydown:
    #     ui.notify("d key presses")
    #     self.download_selected_rows()

    def update_aggrid(self):
        """Convert self.file_list -> row data for AG Grid."""
        row_data = []
        for f in self.file_list:
            raw_name = f.get("filename", "")
            filehash = f.get("filehash", "")
            web_path = f.get("filepath", "")  # e.g. "/static/file.exe"
            # clickable_link = (
            #     f"<a href='{Config.API_HOST}/{web_path}' target='_blank'>{raw_name}</a>"
            # )
            row_data.append(
                {
                    "Filename": raw_name,
                    "Hash": filehash,
                    # has a / in between the 2
                    "WebPath": f"{Config.API_HOST}{web_path}",
                }
            )
        self.aggrid_element.options["rowData"] = row_data
        self.aggrid_element.update()

    def render(self):
        """
        Main render method: sets up the page background, headers, and two tabs.
        """
        self.render_help_button()
        # could combile this and render_files_tab prolly
        self.render_files_tab()
        # Initial data load
        self.on_refresh()

    def render_files_tab(self):
        """
        The 'Files' tab: AG Grid, Refresh, Delete.
        """
        # Create the AG Grid with row selection
        current_settings = app.storage.user.get("settings", {})
        aggrid_theme = (
            "ag-theme-balham-dark"
            if current_settings.get("Dark Mode", False)
            else "ag-theme-balham"
        )

        ui.button(
            text="Build Agent",
            on_click=lambda: self.render_build_agent_dialogue(),
        ).classes("w-full")

        with ui.column().classes("w-full h-full overflow-auto"):
            self.aggrid_element = ui.aggrid(
                {
                    "columnDefs": [
                        {
                            "headerName": "",
                            "checkboxSelection": True,
                            "headerCheckboxSelection": True,
                            "width": 25,
                            "pinned": "left",
                            "floatingFilter": True,
                        },
                        {
                            "headerName": "Filename (name_type_arch_callbackhost_callbackport)",
                            "field": "Filename",
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                            "width": 225,
                        },
                        # { # would take extra tracking, just including in name of agent for now.
                        #     "headerName": "Callback Address",
                        #     "field": "CallbackAddress",
                        #     "filter": "agTextColumnFilter",
                        #     "floatingFilter": True,
                        #     "width": 200,
                        # },
                        # {
                        #     "headerName": "Callback Port",
                        #     "field": "CallbackPort",
                        #     "filter": "agTextColumnFilter",
                        #     "floatingFilter": True,
                        #     "width": 100,
                        # },
                        {
                            "headerName": "Hash (MD5)",
                            "field": "Hash",
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                            "width": 150,
                        },
                        {
                            "headerName": "Web Path",
                            "field": "WebPath",
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                            "width": 300,
                        },
                    ],
                    "rowSelection": "multiple",
                    "rowData": [],
                },
                html_columns=[1],
            ).classes(f"{aggrid_theme} w-full h-full")
            ui.label(
                "WARNING: This endpoint is currently unauth, due to a ui.download problem with nicegui, which does not allow adding headers to a request. TLDR: Anyone who can reach the server, can access any payload you generate/see above, if they know the filename"
            )

        # Refresh / Delete row, keep it below the aggrid
        with ui.row().classes("w-full justify-end gap-4 mt-4"):
            ui.button("Refresh", on_click=self.on_refresh).props("outline")
            ui.button("Delete Selected", on_click=self.delete_selected_rows).props(
                "outline"
            )

            ui.button(  # later have an aggrid on click that runs the download_selected_rows
                "Download Selected", on_click=self.download_selected_rows
            ).props(
                "outline"
            )
            ui.button(  # later have an aggrid on click that runs the download_selected_rows
                "Upload files", on_click=self.render_upload_button_dialog
            ).props(
                "outline"
            )

    async def delete_selected_rows(self):
        rows = await self.aggrid_element.get_selected_rows()
        if rows:
            for row in rows:
                filename = row.get("Filename", "")
                ui.notify(f"Deleted: {filename}", position="top-right")
                url = f"/build/delete/{filename}"
                api_delete_call(url=url)
                # trigger refresh
                self.on_refresh()
        else:
            ui.notify("No rows selected.", position="top-right")

    async def download_selected_rows(self):
        rows = await self.aggrid_element.get_selected_rows()
        if rows:
            for row in rows:
                filename = row.get("Filename", "")
                ui.notify(f"Downloading: {filename}", position="top-right")
                url = f"{Config.API_HOST}/build/{filename}"
                ui.download(url)
                # trigger refresh
                self.on_refresh()
        else:
            ui.notify("No rows selected.", position="top-right")

    # def render_agents_tab(self):
    #     # just importing instead of copying full code
    #     a = AgentsView()
    #     a.render()

    async def render_build_agent_dialogue(self):
        """
        Opens a dialog for building a new agent
        When the user submits, the dialog closes and spawn_listener() is called with values from the dialog.


        Need: Endpoint for current agent types to build. Use this for a dropdown. Usees whats in  the folder to serve which

        """
        # Create the dialog and its contents
        with ui.dialog() as dialog, ui.card():

            # Get listeners options, from data key
            agent_template_options = api_call(url="/build/agent-templates").get(
                "data", ""
            )

            ui.label("Build a new Agent")
            # Input fields for the dialog
            with ui.element().classes("w-full"):  # Ensure full width
                name_input = ui.input(label="[OPT] Agent Name (blank = random name)")
                agent_type_input = ui.select(
                    options=agent_template_options,
                    label="[REQ] Agent Type",
                    on_change=lambda e: update_build_scripts(),  # ui.notify("HI"),  # update_build_scripts(),
                )
                address_input = ui.input(label="[REQ] Callback Address")
                port_input = ui.input(label="[REQ] Port Callback")
                build_script_input = ui.select(
                    options=[],
                    label="[REQ] Build Scripts (select an agent first)",
                )

                def update_build_scripts():
                    agent_type = agent_type_input.value
                    if agent_type:  # Ensure agent type is selected
                        build_script_options = self.fetch_build_scripts(agent_type)
                        build_script_input.options = build_script_options
                        build_script_input.update()  # Refresh UI
                        # ui.notify(
                        #     f"Updated build script options: {build_script_options}"
                        # )  # Debugging log

            with ui.row():
                # When "Submit" is clicked, the dialog is closed and returns a dict of values. kinda weird
                ui.button(
                    "Build Agent",
                    on_click=lambda: dialog.submit(
                        {
                            "agent_name": name_input.value,
                            "agent_type": agent_type_input.value,
                            "callback_port": port_input.value,
                            "callback_address": address_input.value,
                            "build_script": build_script_input.value,
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
            self.build_agent(
                agent_name=result.get("agent_name", ""),
                agent_type=result.get("agent_type", ""),
                callback_address=result.get("callback_address", ""),
                callback_port=result.get("callback_port", ""),
                build_script=result.get("build_script", ""),
            )
        else:
            ui.notify("Agent Builder was canceled.", position="top-right")

    async def render_shellcode_converter_dialogue(self):
        """
        Opens a dialog for building a new agent
        When the user submits, the dialog closes and spawn_listener() is called with values from the dialog.


        Need: Endpoint for current agent types to build. Use this for a dropdown. Usees whats in  the folder to serve which

        """
        # Create the dialog and its contents
        with ui.dialog() as dialog, ui.card():

            # Get listeners options, from data key
            agent_template_options = api_call(url="/build/agent-templates").get(
                "data", ""
            )

            ui.label("Build a new Agent")
            # Input fields for the dialog
            with ui.element().classes("w-full"):  # Ensure full width
                name_input = ui.input(label="[OPT] Agent Name (blank = random name)")
                agent_type_input = ui.select(
                    options=agent_template_options,
                    label="[REQ] Agent Type",
                    on_change=lambda e: update_build_scripts(),  # ui.notify("HI"),  # update_build_scripts(),
                )
                address_input = ui.input(label="[REQ] Callback Address")
                port_input = ui.input(label="[REQ] Port Callback")
                build_script_input = ui.select(
                    options=[],
                    label="[REQ] Build Scripts (select an agent first)",
                )

                def update_build_scripts():
                    agent_type = agent_type_input.value
                    if agent_type:  # Ensure agent type is selected
                        build_script_options = self.fetch_build_scripts(agent_type)
                        build_script_input.options = build_script_options
                        build_script_input.update()  # Refresh UI
                        # ui.notify(
                        #     f"Updated build script options: {build_script_options}"
                        # )  # Debugging log

            with ui.row():
                # When "Submit" is clicked, the dialog is closed and returns a dict of values. kinda weird
                ui.button(
                    "Build Agent",
                    on_click=lambda: dialog.submit(
                        {
                            "agent_name": name_input.value,
                            "agent_type": agent_type_input.value,
                            "callback_port": port_input.value,
                            "callback_address": address_input.value,
                            "build_script": build_script_input.value,
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
            self.build_agent(
                agent_name=result.get("agent_name", ""),
                agent_type=result.get("agent_type", ""),
                callback_address=result.get("callback_address", ""),
                callback_port=result.get("callback_port", ""),
                build_script=result.get("build_script", ""),
            )
        else:
            ui.notify("Agent Builder was canceled.", position="top-right")

    # Example function to be called with the dialog values
    def build_agent(
        self,
        agent_name: str,
        agent_type: str,
        callback_address: str,
        callback_port: str,
        build_script: str,
    ):
        ui.notify("Build started, wait a few seconds and refresh", position="top-right")
        # network call + stuff

        build_dict = {
            "agent_name": agent_name,
            "agent_type": agent_type,
            "callback_address": callback_address,
            "callback_port": callback_port,
            "build_script": build_script,
        }

        # api_post_call(data=listener_dict, url="/plugin/beacon-http/listener/spawn")
        api_post_call(url=f"/build/{agent_type}/build", data=build_dict)

    def fetch_build_scripts(self, agent_type: str):
        print("UPDATING")
        if agent_type:  # Ensure agent_type is not empty or None
            return api_call(url=f"/build/{agent_type}/scripts").get("data", [])
        return []

    async def render_upload_button_dialog(self):
        """ """
        # Create the dialog and its contents
        with ui.dialog() as dialog, ui.card():
            ui.upload(multiple=True, auto_upload=True, on_upload=self.upload_file)
            # with ui.element().classes("w-full"):  # Ensure full width
            # ui.notify("open")
            # ui.label("Upload files")
            # ui.upload()
            # with ui.row():
            #     # When "Submit" is clicked, the dialog is closed and returns a dict of values. kinda weird
            #     ui.button()

        # Actually open dialog
        dialog.open()
        # and refresh on close
        # self.on_refresh()

        result = await dialog
        if result is None:
            """
            Hacky way to on close, becasue we are not submitting anything, refresh grid.
            """
            #
            self.on_refresh()

    def upload_file(self, upload_result):
        """Send uploaded file(s) to POST /build/upload."""
        files = {
            "file": (upload_result.name, upload_result.content),
        }
        data = {}
        # replace with payload upload
        resp = api_post_call("/build/upload", data=data, files=files)
        if not resp or resp.get("status") != 200:
            ui.notify(
                f"Upload failed: {resp.get('message', 'Unknown error')}",
                type="negative",
                position="top-right",
            )
        else:
            ui.notify(
                "File uploaded successfully!", type="positive", position="top-right"
            )

    async def open_help_dialog(self) -> None:
        """Open a help dialog with instructions for the shellcode converter."""
        with ui.dialog().classes("w-full").props("full-width") as dialog, ui.card():
            ui.markdown("# Binary Builder Tab:")
            ui.separator()
            ui.markdown(
                """
                This is the spot for all of your payloads to live. You can upload, donwload, and even generate new payloads on this page.
                
                To generate a payload, click the 'Build Agent' button, and fill in relevant details.

                Additinally, this page supports multi-select, meaning you can do actions on multiple items at once. 
                """
            )
        dialog.open()
        await dialog

    def render_help_button(self) -> None:
        """Render a help button pinned at the bottom-right of the screen."""
        help_button = ui.button("?", on_click=self.open_help_dialog)
        help_button.style("position: fixed; bottom: 10px; right: 10px; z-index: 1000;")


class ShellcodeBuildView:
    """
    View for the Shellcode Builder/Converter.

    This view allows users to select payload files (only .EXE, .DLL, .VBA supported),
    configure Donut (shellcode) options, and perform operations such as conversion,
    deletion, download, and file upload via an AG Grid.
    """

    def __init__(self) -> None:
        # List of payload files fetched from the server.
        self.payload_files: list = []
        # Reference to the AG Grid element.
        self.ag_grid = None
        # Options for shellcode conversion.
        self.shellcode_options: dict = {
            "bypass_options": 1,  # 1: No Bypass, 2: Exit on Failed Bypass, 3: Continue on Failed Bypass
            "output_filename": None,
            "auto_stage": True,
            "architecture": 3,  # 1: x86, 2: amd64, 3: x86/amd64 (default)
        }

    def fetch_payload_files(self) -> None:
        """Fetch the list of compiled payload files from the server."""
        response = api_call("/build/compiled")
        self.payload_files = response.get("data", [])

    def refresh_view(self) -> None:
        """Refresh the payload list and update the AG Grid."""
        self.fetch_payload_files()
        self.update_ag_grid()

    async def open_help_dialog(self) -> None:
        """Open a help dialog with instructions for the shellcode converter."""
        with ui.dialog().classes("w-full").props("full-width") as dialog, ui.card():
            ui.markdown("# Shellcode Converter Page:")
            ui.separator()
            ui.label(
                "This module converts any .EXE, .DLL, or .VBA into shellcode using Donut Loader."
            )
            ui.markdown(
                """
                There are 3 steps:
                
                1. Upload or select the payload you want to convert from the left side.
                2. Select Donut options from the right side.
                3. Click the 'Convert' button. The .bin shellcode should appear in the payload list shortly.
                
                If 'Auto Stage' is enabled, the .bin file will be auto staged at:
                http://\<ip\_of\_server\>:\<port\_of\_server\>/static/\<filename\>.bin
                Manage staged files via the "Hosted Files" section.
                """
            )
        dialog.open()
        await dialog

    def render_help_button(self) -> None:
        """Render a help button pinned at the bottom-right of the screen."""
        help_button = ui.button("?", on_click=self.open_help_dialog)
        help_button.style("position: fixed; bottom: 10px; right: 10px; z-index: 1000;")

    def render(self) -> None:
        """Render the complete Shellcode Builder/Converter UI."""
        current_settings = app.storage.user.get("settings", {})
        with ui.row().classes("w-full h-full flex"):
            self.render_help_button()
            # Left: Payload selection
            with ui.column().classes("flex-1 h-full"):
                with ui.row().classes("items-center justify-between w-full"):
                    ui.label(
                        "1. Select (or upload) payload to convert - only .EXE, .DLL, .VBA supported"
                    ).classes("h6")
                ui.separator()
                with ui.column().classes("flex-1 h-full w-full"):
                    self.render_payloads_grid()
            # Right: Shellcode options and conversion trigger
            with ui.column().classes("flex-1 h-full"):
                with ui.row().classes("items-center justify-between w-full"):
                    ui.label("2. Select Donut options:").classes("h6")
                ui.separator()
                with ui.column().classes("flex-1 h-full w-full"):
                    self.render_shellcode_options_view()
                ui.button("Convert", on_click=self.submit_payload_to_convert).classes(
                    "w-full"
                )
        self.refresh_view()

    def update_ag_grid(self) -> None:
        """Update the AG Grid with the current payload files."""
        row_data = []
        for file_info in self.payload_files:
            filename = file_info.get("filename", "")
            file_hash = file_info.get("filehash", "")
            web_path = file_info.get("filepath", "")  # e.g., "/static/file.exe"
            row_data.append(
                {
                    "Filename": filename,
                    "Hash": file_hash,
                    "WebPath": f"{Config.API_HOST}{web_path}",
                }
            )
        if self.ag_grid:
            self.ag_grid.options["rowData"] = row_data
            self.ag_grid.update()

    def render_shellcode_options_view(self) -> None:
        """Render UI elements for configuring shellcode (Donut) options."""
        ui.markdown("#### AMSI Bypass Options")
        radio_bypass_options = (
            ui.radio(
                options={
                    1: "No Bypass",
                    2: "AMSI Bypass - Exit on Failed Bypass",
                    3: "AMSI Bypass - Continue on Failed Bypass",
                },
                on_change=lambda: self.shellcode_options.update(
                    {"bypass_options": radio_bypass_options.value}
                ),
                value=1,
            )
            .props("inline")
            .classes("w-full")
        )
        ui.separator()

        ui.markdown("#### Payload Architecture")
        radio_architecture = (
            ui.radio(
                options={
                    1: "x86",
                    2: "amd64",
                    3: "x86/amd64 (default)",
                },
                on_change=lambda: self.shellcode_options.update(
                    {"architecture": radio_architecture.value}
                ),
                value=3,
            )
            .props("inline")
            .classes("w-full")
        )
        ui.separator()
        ui.markdown("#### .BIN output name (optional)")
        input_bin_name = ui.input(
            on_change=lambda: self.shellcode_options.update(
                {"output_filename": input_bin_name.value}
            )
        )
        ui.separator()
        ui.markdown("#### Misc:")
        checkbox_auto_stage = ui.checkbox(
            "Auto Stage in hosted files",
            value=True,
            on_change=lambda: self.shellcode_options.update(
                {"auto_stage": checkbox_auto_stage.value}
            ),
        )

    def render_payloads_grid(self) -> None:
        """Render the AG Grid containing available payloads."""
        current_settings = app.storage.user.get("settings", {})
        ag_grid_theme = (
            "ag-theme-balham-dark"
            if current_settings.get("Dark Mode", False)
            else "ag-theme-balham"
        )
        with ui.column().classes("w-full h-full overflow-auto"):
            self.ag_grid = ui.aggrid(
                {
                    "columnDefs": [
                        {
                            "headerName": "",
                            "checkboxSelection": True,
                            "headerCheckboxSelection": True,
                            "width": 25,
                            "pinned": "left",
                            "floatingFilter": True,
                        },
                        {
                            "headerName": "Filename (name_type_arch_callbackhost_callbackport)",
                            "field": "Filename",
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                            "width": 225,
                        },
                        {
                            "headerName": "Hash (MD5)",
                            "field": "Hash",
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                            "width": 150,
                        },
                        {
                            "headerName": "Web Path",
                            "field": "WebPath",
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                            "width": 300,
                        },
                    ],
                    "rowSelection": "multiple",
                    "rowData": [],
                },
                html_columns=[1],
            ).classes(f"{ag_grid_theme} w-full h-full")
        with ui.row().classes("w-full justify-end gap-4 mt-4"):
            ui.button("Refresh", on_click=self.refresh_view).props("outline")
            ui.button("Delete Selected", on_click=self.delete_selected_rows).props(
                "outline"
            )
            ui.button("Download Selected", on_click=self.download_selected_rows).props(
                "outline"
            )
            ui.button("Upload Files", on_click=self.render_upload_dialog).props(
                "outline"
            )

    async def delete_selected_rows(self) -> None:
        """Delete selected rows from the AG Grid and refresh the view."""
        selected_rows = await self.ag_grid.get_selected_rows()
        if selected_rows:
            for row in selected_rows:
                filename = row.get("Filename", "")
                ui.notify(f"Deleted: {filename}", position="top-right")
                api_delete_call(url=f"/build/delete/{filename}")
            self.refresh_view()
        else:
            ui.notify("No rows selected.", position="top-right")

    async def download_selected_rows(self) -> None:
        """Download selected payload files and refresh the view."""
        selected_rows = await self.ag_grid.get_selected_rows()
        if selected_rows:
            for row in selected_rows:
                filename = row.get("Filename", "")
                ui.notify(f"Downloading: {filename}", position="top-right")
                download_url = f"{Config.API_HOST}/build/{filename}"
                ui.download(download_url)
            self.refresh_view()
        else:
            ui.notify("No rows selected.", position="top-right")

    async def render_upload_dialog(self) -> None:
        """Render a dialog to upload payload files."""
        with ui.dialog() as dialog, ui.card():
            ui.upload(multiple=True, auto_upload=True, on_upload=self.upload_file)
        dialog.open()
        result = await dialog
        if result is None:
            self.refresh_view()

    def upload_file(self, upload_result) -> None:
        """
        Upload a file to the server.

        Args:
            upload_result: An object with 'name' and 'content' attributes for the uploaded file.
        """
        files = {"file": (upload_result.name, upload_result.content)}
        data = {}
        response = api_post_call("/build/upload", data=data, files=files)
        if not response or response.get("status") != 200:
            ui.notify(
                f"Upload failed: {response.get('message', 'Unknown error')}",
                type="negative",
                position="top-right",
            )
        else:
            ui.notify(
                "File uploaded successfully!", type="positive", position="top-right"
            )

    async def submit_payload_to_convert(self) -> None:
        """
        Submit selected payload(s) for conversion into shellcode.

        Uses the /build/convert-to-shellcode endpoint with the options specified in shellcode_options.
        """
        selected_rows = await self.ag_grid.get_selected_rows()
        if selected_rows:
            for row in selected_rows:
                filename = row.get("Filename", "")
                auto_stage = self.shellcode_options.get("auto_stage", False)
                output_name = self.shellcode_options.get("output_filename")
                conversion_data = {
                    "file_to_convert": filename,
                    "output_file_name": (
                        output_name if output_name else filename.split(".")[0]
                    ),
                    "architecture": self.shellcode_options.get("architecture"),
                    "bypass_options": self.shellcode_options.get("bypass_options"),
                    "auto_stage": auto_stage,
                }
                api_post_call("/build/convert-to-shellcode", data=conversion_data)
                ui.notify("Submitted to convert", position="top-right", type="positive")
                if auto_stage:
                    ui.notify(
                        "Staged file at ...", position="top-right", type="positive"
                    )
        else:
            ui.notify("No payload selected for conversion.", position="top-right")
