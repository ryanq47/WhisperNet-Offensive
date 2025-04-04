from nicegui import ui, app
from datetime import datetime
from networking import api_call, api_post_call, api_delete_call
from config import Config
import asyncio  # If not already imported
import requests
import json
import httpx
import pandas as pd
from io import StringIO


class CredentialStore:
    def __init__(self):
        self.credential_data = []
        self.grid = None

    async def open_help_dialog(self) -> None:
        """Open a help dialog with instructions for the shellcode converter."""
        with ui.dialog().classes("w-full").props("full-width") as dialog, ui.card():
            ui.markdown("# The CredentialStore:")
            ui.separator()
            ui.markdown(
                """
                This is where you can store credentials in Whispernet

                Additionally, you can export, and import creds from a .CSV

                Note: You currently CANNOT copy out of the Aggrid, so you'll
                need to download the .CSV then copy from there. I'm working on fixing this.

                """
            )
            ui.separator()
            ui.markdown(
                """
                #### Usage:
                        
                1. Add info to fields at the top
                2. Click "ADD" to add to the Cred Store.


                Pro Tip: The "Password" and "Notes" fields support newlines/multiline,
                so you can paste an entire mimikatz dump, or other large password dumps in there.

                NewLines will NOT render *in* the AgGrid, but they will when you download the .CSV

                This does make the CSV look a little weird in raw text, but works well when in something such as Excel
                        """
            )
        dialog.open()
        await dialog

    def render_help_button(self) -> None:
        """Render a help button pinned at the bottom-right of the screen."""
        help_button = ui.button("Current Page Info", on_click=self.open_help_dialog)
        help_button.style("position: fixed; top: 170px; right: 24px; ")

    def render(self):
        self.render_help_button()
        with ui.column().classes("w-full h-full p-4"):
            current_settings = app.storage.user.get("settings", {})

            # Page title
            # Add Credential Form
            with ui.row().classes("gap-4 mb-4 items-center w-full"):
                with ui.row().classes("flex-1 gap-4"):
                    self.username_input = ui.input(label="Username").classes("flex-1")
                    self.password_input = (
                        ui.textarea(label="Password")
                        .classes("flex-1")
                        .props("input-class=h-7")  # make height same as rest
                    )
                    self.realm_input = ui.input(label="Realm/Domain").classes("flex-1")
                    self.notes_input = (
                        ui.textarea(label="Notes")
                        .classes("flex-1")
                        .props("input-class=h-7")  # make height same as rest
                    )
                    ui.button("Add", on_click=self.add_credential).classes(
                        "bg-green-500 text-white px-4 py-2 rounded"
                    )

            aggrid_theme = (
                "ag-theme-balham-dark"
                if current_settings.get("Dark Mode", False)
                else "ag-theme-balham"
            )

            # Credential Grid
            self.credential_data = self.get_cred_data()
            self.grid = ui.aggrid(
                {
                    "columnDefs": [
                        {
                            "headerName": "ID",
                            "field": "id",
                            "sortable": True,
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                        },
                        {
                            "headerName": "Username",
                            "field": "username",
                            "sortable": True,
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                        },
                        {
                            "headerName": "Password",
                            "field": "password",
                            "sortable": True,
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                        },
                        {
                            "headerName": "Realm",
                            "field": "realm",
                            "sortable": True,
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                        },
                        {
                            "headerName": "Date Added",
                            "field": "date_added",
                            "sortable": True,
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                        },
                        {
                            "headerName": "Notes",
                            "field": "notes",
                            "sortable": True,
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                        },
                    ],
                    "rowData": self.credential_data,
                    "rowSelection": "multiple",
                    "suppressRowClickSelection": False,
                    "enableRangeSelection": True,
                    # Ensure that copying rows to clipboard is allowed (default is false, so we set it explicitly)
                    "suppressCopyRowsToClipboard": False,
                }
            ).classes(f"{aggrid_theme} h-full")

            # Toolbar
            with ui.row().classes("w-full justify-end gap-4 mt-4"):

                ui.button("Export CSV", on_click=self.export_csv).props("outline")
                ui.button("Delete Selected", on_click=self.delete_selected).props(
                    "outline"
                )
                ui.button(
                    text="Upload CSV",
                    on_click=self.render_upload_button_dialog,
                ).props("accept='.csv' outline")

    async def render_upload_button_dialog(self):
        """ """
        # Create the dialog and its contents
        with ui.dialog() as dialog, ui.card():
            ui.upload(
                multiple=True, auto_upload=True, on_upload=self.process_uploaded_file
            )
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

    def add_credential(self):
        username = self.username_input.value
        password = self.password_input.value
        realm = self.realm_input.value
        notes = self.notes_input.value
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if username and password:
            credential_data = {
                "username": username,
                "password": password,
                "realm": realm,
                "date": date,
                "notes": notes,
            }

        else:
            ui.notify("Username and Password field are required", position="top-right")

        self.add_cred_to_server(data=credential_data)
        self.refresh_grid()
        self.username_input.value = ""
        self.password_input.value = ""
        self.realm_input.value = ""
        self.notes_input.value = ""

    async def delete_selected(self):
        """
        Deletes the selected rows from the grid and updates the data.
        """
        selected_rows = await self.grid.get_selected_rows()

        for row in selected_rows:
            cred_id = row.get("id")  # Ensure "id" exists in row data
            if cred_id:
                api_delete_call(f"/credstore/credential/{cred_id}")

        self.refresh_grid()
        # try:
        #     # Await the coroutine to get selected rows
        #     selected_rows = await self.grid.get_selected_rows()

        #     # Iterate over selected rows and send a DELETE request for each
        #     async with httpx.AsyncClient() as client:
        #         for row in selected_rows:
        #             cred_id = row.get("id")  # Ensure "id" exists in row data
        #             if cred_id:
        #                 try:
        #                     response = await client.delete(
        #                         f"/credstore/credential/{cred_id}"
        #                     )
        #                     if response.status_code != 200:
        #                         print(
        #                             f"Failed to delete credential ID {cred_id}: {response.text}"
        #                         )
        #                 except Exception as request_error:
        #                     print(
        #                         f"Error deleting credential ID {cred_id}: {request_error}"
        #                     )

        #     # # Filter out the selected rows from the credential data
        #     # self.credential_data = [
        #     #     row for row in self.credential_data if row not in selected_rows
        #     # ]

        #     # Refresh the grid to reflect the updated data
        #     self.refresh_grid()
        # except Exception as e:
        #     print(f"Error deleting selected rows: {e}")

    def refresh_grid(self):
        """
        Refresh the ag-Grid with updated row data.
        """
        try:
            # # Ensure the grid is updated with the new row data
            # self.grid.options["rowData"] = (
            #     self.credential_data
            # )  # Update grid data directly
            # self.get_cred_data()
            # DOESN"T UPDATE AHHH

            # temporarily reload page, instead of just aggrid
            ui.navigate.to("/credstore")
            self.grid.update()  # Trigger a grid refresh
        except Exception as e:
            print(f"Error refreshing grid: {e}")

    def get_cred_data(self) -> list:
        try:
            data = api_call(url=f"/credstore/credentials")

            # data comes as a list inside the data.credential key.
            return data.get("data").get("credentials")
        except Exception as e:
            ui.notify(f"Error fetching credential data: {e}", position="top-right")

    def add_cred_to_server(self, data):
        # headers = {
        #     "Authorization": f"Bearer {app.storage.user.get("jwt_token", "")}",
        #     "Content-Type": "application/json",
        # }

        # r = requests.post(
        #     url=f"/credstore/credential",
        #     json=data,  # data needs to be json string
        #     headers=headers,
        # )
        # if r.status_code == 200 or r.status_code == 201:
        #     ui.notify("Successfully added credential", position="top-right")

        api_post_call("/credstore/credential", data=data)

        # else:
        #     ui.notify(f"{r.status_code} Error adding credential", position="top-right")

    def process_uploaded_file(self, event):
        """
        Process the uploaded file and import credentials.
        """
        try:

            # Access the uploaded file content
            file = StringIO(event.content.read().decode("utf-8"))

            # Read the uploaded CSV file into a DataFrame
            df = pd.read_csv(file)

            # Validate required columns
            required_columns = {"Username", "Password"}
            if not required_columns.issubset(df.columns):
                ui.notify(
                    "CSV must contain 'username' and 'password' columns",
                    color="red",
                    position="top-right",
                )
                return

            # Convert DataFrame to list of dictionaries
            credentials = df.to_dict(orient="records")

            # Send each credential to the server
            for cred in credentials:
                # Keynames are diffrenrt/capatalized as that's how the Aggrid exports them
                data = {
                    "username": cred.get("Username"),
                    "password": cred.get("Password"),
                    "realm": cred.get("Realm", None),
                    "notes": cred.get("Date Added", None),
                }
                self.add_cred_to_server(data)

            # Refresh the grid after import
            # self.refresh_grid()
            ui.notify(
                f"Successfully imported {len(credentials)} credentials",
                color="green",
                position="top-right",
            )
        except Exception as e:
            ui.notify(f"Error processing CSV: {e}", color="red", position="top-right")

    def export_csv(self):
        ui.notify("Prepping data to export...")
        self.grid.run_grid_method("exportDataAsCsv")


class CredentialStorePage:
    def __init__(self): ...

    def render(self):
        with ui.column().classes("w-full h-full p-[10px]"):
            # HEADER 1
            with ui.row().classes("w-full text-5xl"):
                ui.icon("key")
                ui.label("Credentials").classes("h-10")

            # HEADER 2
            with ui.row().classes("w-full text-2xl"):
                ui.icon("info")
                ui.label("Store and Access credentials").classes("h-6")
                ui.space()
            ui.separator()

            # -- TABS --
            with ui.tabs() as tabs:
                ui.tab("Credentials")
                # ui.tab("Import Creds")

            # -- TAB PANELS --
            with ui.tab_panels(tabs, value="Credentials").classes(
                "w-full h-full border"
            ):
                with ui.tab_panel("Credentials").classes("h-full"):
                    a = CredentialStore()
                    a.render()
                # with ui.tab_panel("Import Creds"):
                #     a = CredentialStore()
                #     a.render()
                # with ui.tab_panel("Scripts"):
                #     a = ScriptsView()
                #     a.render()
