from nicegui import ui, app
from datetime import datetime
from networking import api_call
from config import Config
import asyncio  # If not already imported
import requests
import json


class CredentialStore:
    def __init__(self):
        self.credential_data = []
        self.grid = None

    def render(self):
        with ui.column().classes("w-full p-4 border"):
            ui.label("Credential Store").classes("text-2xl text-center mb-4")

            # Add Credential Form
            with ui.row().classes("gap-4 mb-4 items-center w-full"):
                with ui.row().classes("flex-1 gap-4"):
                    self.username_input = ui.input(label="Username").classes("flex-1")
                    self.password_input = ui.input(label="Password").classes("flex-1")
                    self.realm_input = ui.input(label="Realm/Domain").classes("flex-1")
                    self.notes_input = ui.input(label="Notes").classes("flex-1")
                ui.button("Add", on_click=self.add_credential).classes(
                    "bg-green-500 text-white"
                )

            self.credential_data = self.get_cred_data()
            # print(self.credential_data)

            # Credential Grid with Search Filters
            self.grid = ui.aggrid(
                {
                    "columnDefs": [
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
                            "headerName": "Realm/Domain",
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
                    "rowSelection": "multiple",  # Enable multi-row selection
                    "suppressRowClickSelection": False,  # Allow row clicks to select
                }
            ).style("height: 400px; width: 100%;")

            # Action Buttons
            with ui.row().classes("gap-4 mt-4"):
                ui.button("Delete Selected", on_click=self.delete_selected).classes(
                    "bg-red-500 text-white"
                )
                ui.button("Export CSV", on_click=self.export_csv).classes(
                    "bg-blue-500 text-white"
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
            ui.notify("Username and Password field are required")

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
        try:
            # Await the coroutine to get selected rows
            selected_rows = await self.grid.get_selected_rows()

            # get ID, for each id selected, send delete when hit delete

            # Filter out the selected rows from the credential data
            self.credential_data = [
                row for row in self.credential_data if row not in selected_rows
            ]

            # Refresh the grid to reflect the updated data
            self.refresh_grid()
        except Exception as e:
            print(f"Error deleting selected rows: {e}")

    def refresh_grid(self):
        self.grid.update({"rowData": self.credential_data})

    def get_cred_data(self) -> list:
        try:
            data = api_call(url=f"{Config.API_HOST}/credstore/credentials")

            # data comes as a list inside the data.credential key.
            return data.get("data").get("credentials")
        except Exception as e:
            ui.notify(f"Error fetching credential data: {e}")

    def add_cred_to_server(self, data):
        headers = {
            "Authorization": f"Bearer {app.storage.user.get("jwt_token", "")}",
            "Content-Type": "application/json",
        }

        r = requests.post(
            url=f"{Config.API_HOST}/credstore/credential",
            json=data,  # data needs to be json string
            headers=headers,
        )
        if r.status_code == 200 or r.status_code == 201:
            ui.notify("Successfully added credential")

        else:
            ui.notify(f"{r.status_code} Error adding credential")

    def import_csv(self): ...

    def export_csv(self):
        ui.notify("Prepping data to export...")
        self.grid.run_grid_method("exportDataAsCsv")
