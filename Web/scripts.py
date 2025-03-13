from nicegui import ui, app
from networking import api_call, api_post_call, api_delete_call
from config import Config, ThemeConfig


class ScriptsView:
    def __init__(self): ...

    def render(self):

        with ui.tabs() as tabs:
            ui.tab("Script Files")
            ui.tab("Upload")

        # -- TAB PANELS --
        with ui.tab_panels(tabs, value="Script Files").classes("w-full h-full"):
            with ui.tab_panel("Script Files").classes("h-full"):
                sfv = ScriptsFileView()
                sfv.render()
            with ui.tab_panel("Upload"):
                fuv = FileUploadView()
                fuv.render()


class ScriptsFileView:
    """
    Displays a page for managing files in the static-serve plugin,
    now split into two tabs: 'Files' (AG Grid) and 'Upload'.
    """

    def __init__(self):
        self.file_list = []
        self.aggrid_element = None

    def fetch_file_list(self):
        resp = api_call("scripts/files")
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
            web_path = f.get("filepath", "")  # e.g. "/scripts/file.yaml"
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
                        # {
                        #     "headerName": "Web Path",
                        #     "field": "WebPath",
                        #     "filter": "agTextColumnFilter",
                        #     "floatingFilter": True,
                        #     "width": 300,
                        # },
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

            # borked due to jwt issue
            # ui.button(  # later have an aggrid on click that runs the download_selected_rows
            #     "Download Selected", on_click=self.download_selected_rows
            # ).props(
            #     "outline"
            # )

    async def delete_selected_rows(self):
        rows = await self.aggrid_element.get_selected_rows()
        if rows:
            for row in rows:
                filename = row.get("Filename", "")
                ui.notify(f"Deleted: {filename}", position="top-right")
                url = f"/scripts/delete/{filename}"
                api_delete_call(url=url)
                # trigger refresh
                self.on_refresh()
        else:
            ui.notify("No rows selected.", position="top-right")

    # async def download_selected_rows(self):
    #     rows = await self.aggrid_element.get_selected_rows()
    #     if rows:
    #         for row in rows:
    #             filename = row.get("Filename", "")
    #             ui.notify(f"Downloading: {filename}")
    #             url = f"{Config.API_HOST}/{filename}"
    #             ui.download(url)
    #             # trigger refresh
    #             self.on_refresh()
    #     else:
    #         ui.notify("No rows selected.")


class FileUploadView:
    def __init__(self):
        pass

    def render(self):
        """
        The 'Upload' tab: a big area for uploading.
        """
        with ui.column().classes("w-full h-full items-center"):
            ui.upload(
                label="Upload File(s)",
                on_upload=self.on_file_upload,
                auto_upload=True,
                multiple=True,
            ).classes("w-full h-full").props("accept=.yaml")
            # note, the accept is not a true protector for filetype uploads, need to secure API as well.

            ui.label("Drag N Drop, or click the '+'")

    def on_file_upload(self, upload_result):
        """Send uploaded file(s) to POST /scripts/upload."""
        files = {
            "file": (upload_result.name, upload_result.content),
        }
        data = {}
        resp = api_post_call("scripts/upload", data=data, files=files)
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

        # Refresh after each file upload
        # self.on_refresh()
