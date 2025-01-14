from nicegui import ui
from networking import api_call
from config import Config


class LogsView:
    def __init__(self):
        self.html_log_data = api_call(f"{Config.API_HOST}/stats/logs/html")
        self.text_log_data = api_call(f"{Config.API_HOST}/stats/logs/html")

    def render(self):
        ui.label("gaps.... gaps for days")
        with ui.column().classes(
            "w-full h-5/6 flex flex-col p-4 gap-4 absolute-center"
        ):
            with ui.card().classes("w-full h-5/6 p-4 shadow-md flex flex-col"):
                ui.label("Logs Viewer").classes("text-2xl font-bold mb-4 text-center")
                ui.separator()

                # Logs Display
                with ui.scroll_area().classes("flex-1 overflow-y-auto"):
                    self.logs_container = ui.html(self.html_log_data)

                with ui.row().classes("justify-center w-full mt-4 gap-4"):
                    ui.button(
                        "Export HTML Logs", on_click=self._export_html_logs
                    ).props("flat").classes("flex-1")
                    ui.button(
                        "Export Text Logs", on_click=self._export_text_logs
                    ).props("flat").classes("flex-1")

    def _export_html_logs(self):
        # get data at export, instead of at init
        html_log_data = api_call(f"{Config.API_HOST}/stats/logs/html")
        # Provide logs as a downloadable file
        with open("logs_export.html", "w") as f:
            f.write(html_log_data)
        ui.download("logs_export.html", "LogsExport.html")

    def _export_text_logs(self):
        # get data at export, instead of at init
        text_log_data = api_call(
            f"{Config.API_HOST}/stats/logs/text", return_dict_from_json=False
        )
        # Provide logs as a downloadable file
        with open("logs_export.txt", "w") as f:
            f.write(text_log_data)
        ui.download("logs_export.txt", "LogsExport.txt")
