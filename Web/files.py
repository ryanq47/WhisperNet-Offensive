from nicegui import ui, app
import requests
from config import Config
from networking import api_call, api_post_call, api_delete_call


class FilePage:
    def __init__(self):
        pass

    def render(self):
        with ui.column().classes("w-full h-full p-[10px]"):
            # HEADER 1
            with ui.row().classes("w-full text-5xl"):
                ui.icon("dns")
                ui.label("Files").classes("h-10")

            # HEADER 2
            with ui.row().classes("w-full text-2xl"):
                ui.icon("warning")
                ui.label(
                    "Hosted Files - Publicly available to anyone who can access the server address"
                ).classes("h-6")
                ui.space()
            ui.separator()

            # -- TABS --
            with ui.tabs() as tabs:
                ui.tab("Files")
                # ui.tab("Upload")

            # -- TAB PANELS --
            with ui.tab_panels(tabs, value="Files").classes("w-full h-full border"):
                with ui.tab_panel("Files").classes("h-full"):
                    a = FileView().render()
                # with ui.tab_panel("Upload"):
                #     a = FileUploadView().render()


## Filevliew


class FileView:
    """
    Displays a page for managing files in the static-serve plugin,
    now split into two tabs: 'Files' (AG Grid) and 'Upload'.
    """

    def __init__(self):
        self.file_list = []
        self.aggrid_element = None

    async def open_help_dialog(self) -> None:
        """Open a help dialog with instructions for the shellcode converter."""
        with ui.dialog().classes("w-full").props("full-width") as dialog, ui.card():
            ui.markdown("# Hosted Files Tab:")
            ui.separator()
            ui.markdown(
                """
                This is where hosted files live. 

                Any file you wish to host/retrieve from the server should go here. 

                Additionally, this supports multi-select, so actions can be take on multiple files at once

                To upload a file, click the `UPLOAD` button and either drag & drop files in, or select the '+' for a file menu.
                 - Note: The files will auto-upload when selected.
                """
            )
        dialog.open()
        await dialog

    def render_help_button(self) -> None:
        """Render a help button pinned at the bottom-right of the screen."""
        help_button = ui.button("Current Page Info", on_click=self.open_help_dialog)
        help_button.style("position: fixed; top: 170px; right: 24px; ")

    def fetch_file_list(self):
        resp = api_call("static-serve/files")
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
                    # has a / inbetween the 2
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

        with ui.column().classes("w-full h-full overflow-auto"):
            self.aggrid_element = ui.aggrid(
                {
                    "columnDefs": [
                        {
                            "headerName": "",
                            "checkboxSelection": True,
                            "headerCheckboxSelection": True,
                            "width": 30,
                            "pinned": "left",
                            "floatingFilter": True,
                        },
                        {
                            "headerName": "Filename",
                            "field": "Filename",
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                            "width": 250,
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
            ).classes(f"{aggrid_theme} w-full h-full")

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
                url = f"/static-serve/delete/{filename}"
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
                url = f"{Config.API_HOST}/{filename}"
                ui.download(url)
                # trigger refresh
                self.on_refresh()
        else:
            ui.notify("No rows selected.", position="top-right")

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

    async def upload_file(self, upload_result):
        """Send uploaded file(s) to POST /static-serve/upload."""
        files = {
            "file": (upload_result.name, upload_result.content),
        }
        data = {}
        resp = api_post_call("static-serve/upload", data=data, files=files)
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
