from nicegui import ui
from networking import api_call
from config import Config


class LogsView:
    def __init__(self):
        self.html_log_data = api_call(f"{Config.API_HOST}/stats/logs/html")
        self.text_log_data = api_call(f"{Config.API_HOST}/stats/logs/html")

    def render(self):
        # Navbar
        with ui.header().classes(
            "items-center justify-between bg-neutral-800 h-16 px-4"
        ):
            ui.button("Back", on_click=lambda: ui.open("/")).props("flat color=white")
            ui.label("Logs Viewer").classes("text-white text-xl")

        # Main Content
        with ui.column().classes("w-full items-center p-4 gap-4"):
            # Logs Viewer Card
            with ui.card().classes("w-full max-w-screen-lg p-4 shadow-md"):
                ui.label("Logs Viewer").classes("text-2xl font-bold mb-4 text-center")
                ui.separator()

                # Search Bar
                ui.input(placeholder="Search logs...").on(
                    "input", self._search_logs
                ).props("outlined").classes("mb-4 w-full")

                # Logs Display
                self.logs_container = ui.html(self.html_log_data).classes(
                    "overflow-auto p-4 border rounded-lg max-h-96"
                )

                with ui.row().classes("justify-center w-full mt-4 gap-4"):
                    ui.button(
                        "Export HTML Logs", on_click=self._export_html_logs
                    ).props("flat").classes("flex-1")
                    ui.button(
                        "Export Text Logs", on_click=self._export_text_logs
                    ).props("flat").classes("flex-1")

    def _search_logs(self, event):
        search_term = event.value.lower()
        filtered_logs = [
            line for line in self.log_data.splitlines() if search_term in line.lower()
        ]
        self.logs_container.set_content("<br>".join(filtered_logs))

    def _export_html_logs(self):
        # get data at export, instead of at init
        html_log_data = api_call(f"{Config.API_HOST}/stats/logs/html")
        # Provide logs as a downloadable file
        with open("logs_export.html", "w") as f:
            f.write(html_log_data)
        ui.download("logs_export.html", "LogsExport.html")

    def _export_text_logs(self):
        # get data at export, instead of at init
        text_log_data = api_call(f"{Config.API_HOST}/stats/logs/html")
        # Provide logs as a downloadable file
        with open("logs_export.txt", "w") as f:
            f.write(text_log_data)
        ui.download("logs_export.txt", "LogsExport.txt")
