from nicegui import ui
from datetime import datetime


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
                            "headerName": "Date",
                            "field": "date",
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
            self.credential_data.append(
                {
                    "username": username,
                    "password": password,
                    "realm": realm,
                    "date": date,
                    "notes": notes,
                }
            )
            self.refresh_grid()
            self.username_input.value = ""
            self.password_input.value = ""
            self.realm_input.value = ""
            self.notes_input.value = ""

    def delete_selected(self):
        selected_rows = self.grid.get_selected_rows()
        self.credential_data = [
            row for row in self.credential_data if row not in selected_rows
        ]
        self.refresh_grid()

    def refresh_grid(self):
        self.grid.update({"rowData": self.credential_data})

    def export_csv(self):
        self.grid.run_grid_method("exportDataAsCsv")
