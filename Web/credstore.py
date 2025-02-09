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

    def render(self):
        with ui.column().classes("w-full h-full p-4 border"):
            # Page title
            ui.label("Credential Store").classes("text-2xl text-center mb-4")

            # Add Credential Form
            with ui.row().classes("gap-4 mb-4 items-center w-full"):
                with ui.row().classes("flex-1 gap-4"):
                    self.username_input = ui.input(label="Username").classes("flex-1")
                    self.password_input = ui.input(label="Password").classes("flex-1")
                    self.realm_input = ui.input(label="Realm/Domain").classes("flex-1")
                    self.notes_input = ui.input(label="Notes").classes("flex-1")
                ui.button("Add", on_click=self.add_credential).classes(
                    "bg-green-500 text-white px-4 py-2 rounded"
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
                }
            ).style("height: 400px; width: 100%;")

            # Toolbar
            with ui.row().classes(
                "w-full gap-4 py-2 bg-gray-100 border-b items-center justify-center"
            ):
                ui.button("Export CSV", on_click=self.export_csv).classes(
                    "bg-blue-500 text-white px-4 py-2 rounded flex-1"
                )
                ui.button("Delete Selected", on_click=self.delete_selected).classes(
                    "bg-red-500 text-white px-4 py-2 rounded flex-1"
                )

            ui.upload(
                label="Import CSV",
                on_upload=self.process_uploaded_file,
            ).props(
                "accept='.csv'"
            ).classes("bg-blue-400 text-white px-4 py-2 rounded w-full")

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

            # Iterate over selected rows and send a DELETE request for each
            async with httpx.AsyncClient() as client:
                for row in selected_rows:
                    cred_id = row.get("id")  # Ensure "id" exists in row data
                    if cred_id:
                        try:
                            response = await client.delete(
                                f"{Config.API_HOST}/credstore/credential/{cred_id}"
                            )
                            if response.status_code != 200:
                                print(
                                    f"Failed to delete credential ID {cred_id}: {response.text}"
                                )
                        except Exception as request_error:
                            print(
                                f"Error deleting credential ID {cred_id}: {request_error}"
                            )

            # # Filter out the selected rows from the credential data
            # self.credential_data = [
            #     row for row in self.credential_data if row not in selected_rows
            # ]

            # Refresh the grid to reflect the updated data
            self.refresh_grid()
        except Exception as e:
            print(f"Error deleting selected rows: {e}")

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
            )
        except Exception as e:
            ui.notify(f"Error processing CSV: {e}", color="red")

    def export_csv(self):
        ui.notify("Prepping data to export...")
        self.grid.run_grid_method("exportDataAsCsv")
