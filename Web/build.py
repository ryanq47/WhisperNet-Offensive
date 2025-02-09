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

    async def delete_selected_rows(self):
        rows = await self.aggrid_element.get_selected_rows()
        if rows:
            for row in rows:
                filename = row.get("Filename", "")
                ui.notify(f"Deleted: {filename}")
                url = f"/build/delete/{filename}"
                api_delete_call(url=url)
                # trigger refresh
                self.on_refresh()
        else:
            ui.notify("No rows selected.")

    async def download_selected_rows(self):
        rows = await self.aggrid_element.get_selected_rows()
        if rows:
            for row in rows:
                filename = row.get("Filename", "")
                ui.notify(f"Downloading: {filename}")
                url = f"{Config.API_HOST}/build/{filename}"
                ui.download(url)
                # trigger refresh
                self.on_refresh()
        else:
            ui.notify("No rows selected.")

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

            ui.label("Spawn a New Listener")
            # Input fields for the dialog
            with ui.element().classes(
                "w-full"
            ):  # make sure fields are full width of parent dialogue container
                name_input = ui.input(label="Agent Name (blank = random name)")
                agent_type_input = ui.select(
                    options=agent_template_options, label="Agent Type"
                )  # ui.input(label="Agent Type")
                address_input = ui.input(label="Callback Address")
                port_input = ui.input(label="Port Callback")

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
            )
        else:
            ui.notify("Agent Builder was canceled.")

    # Example function to be called with the dialog values
    def build_agent(
        self,
        agent_name: str,
        agent_type: str,
        callback_address: str,
        callback_port: str,
    ):
        ui.notify("Build started, wait a few seconds and refresh")
        # network call + stuff

        build_dict = {
            "agent_name": agent_name,
            "agent_type": agent_type,
            "callback_address": callback_address,
            "callback_port": callback_port,
        }

        # api_post_call(data=listener_dict, url="/plugin/beacon-http/listener/spawn")
        api_post_call(url=f"/build/{agent_type}/build", data=build_dict)
