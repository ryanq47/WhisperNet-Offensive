from nicegui import ui, app
import requests
from config import Config


# ---------------------------
#   API Helper Functions
# ---------------------------
def api_call(url, timeout=3):
    """
    Makes a synchronous GET request to the specified endpoint.
    Automatically attaches the JWT token. Returns parsed JSON or raises on error.
    """
    if not url:
        raise ValueError("A valid endpoint path must be provided.")

    endpoint = f"{Config.API_HOST}/{url.lstrip('/')}"
    jwt_token = app.storage.user.get("jwt_token", "")
    headers = {
        "Authorization": f"Bearer {jwt_token}",
    }

    try:
        r = requests.get(endpoint, headers=headers, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.JSONDecodeError:
        raise ValueError("The response is not valid JSON.")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        ui.notify(f"Request failed: {e}", type="negative")
        return {}


def api_post_call(url, data=None, files=None):
    """
    Sends a POST request to the specified endpoint.
      - If 'files' is provided, send as multipart/form-data.
      - Otherwise, send 'data' as JSON.
    Returns the parsed JSON response (if any), or an empty dict on error.
    """
    endpoint = f"{Config.API_HOST}/{url.lstrip('/')}"
    jwt_token = app.storage.user.get("jwt_token", "")
    headers = {
        "Authorization": f"Bearer {jwt_token}",
    }

    try:
        if files:
            # Multipart/form-data request (for file uploads)
            r = requests.post(url=endpoint, data=data, files=files, headers=headers)
        else:
            # JSON-only request
            headers["Content-Type"] = "application/json"
            r = requests.post(url=endpoint, json=data, headers=headers)

        if r.status_code not in (200, 201):
            try:
                error_message = r.json().get("message", r.text)
            except Exception:
                error_message = r.text
            ui.notify(f"Error {r.status_code}: {error_message}", type="negative")
            return {}

        try:
            resp_json = r.json()
            ui.notify("Request succeeded", type="positive")
            return resp_json
        except Exception:
            ui.notify("Request succeeded, but no JSON in response", type="warning")
            return {}
    except Exception as e:
        ui.notify(f"Request exception: {str(e)}", type="negative")
        return {}


def api_delete_call(url):
    """
    Sends a DELETE request to the specified endpoint.
    Returns the parsed JSON response (if any), or an empty dict on error.
    """
    endpoint = f"{Config.API_HOST}/{url.lstrip('/')}"
    jwt_token = app.storage.user.get("jwt_token", "")
    headers = {"Authorization": f"Bearer {jwt_token}"}

    try:
        r = requests.delete(endpoint, headers=headers)
        if r.status_code not in (200, 201):
            try:
                error_message = r.json().get("message", r.text)
            except Exception:
                error_message = r.text
            ui.notify(f"Error {r.status_code}: {error_message}", type="negative")
            return {}
        return r.json() if r.text else {}
    except Exception as e:
        ui.notify(f"Request exception: {str(e)}", type="negative")
        return {}


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
                ui.tab("Upload")

            # -- TAB PANELS --
            with ui.tab_panels(tabs, value="Files").classes("w-full h-full border"):
                with ui.tab_panel("Files").classes("h-full"):
                    a = FileView().render()
                with ui.tab_panel("Upload"):
                    a = FileUploadView().render()


## Filevliew


class FileView:
    """
    Displays a page for managing files in the static-serve plugin,
    now split into two tabs: 'Files' (AG Grid) and 'Upload'.
    """

    def __init__(self):
        self.file_list = []
        self.aggrid_element = None

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
            clickable_link = (
                f"<a href='{Config.API_HOST}/{web_path}' target='_blank'>{raw_name}</a>"
            )
            row_data.append(
                {
                    "FilenameLink": clickable_link,
                    "FilenameRaw": raw_name,
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
                            "width": 50,
                            "pinned": "left",
                            "floatingFilter": True,
                        },
                        {
                            "headerName": "Filename",
                            "field": "FilenameLink",
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                            "width": 250,
                        },
                        {
                            "headerName": "Hash (MD5)",
                            "field": "Hash",
                            "filter": "agTextColumnFilter",
                            "floatingFilter": True,
                            "width": 240,
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
            ui.button("Delete Selected - BROKEN", on_click=...).props("outline")


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
            ).classes(
                "w-full h-full"
            )  # or "w-full" for an even bigger area

            ui.label("Drag N Drop, or click the '+'")

    def on_file_upload(self, upload_result):
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
            )
        else:
            ui.notify("File uploaded successfully!", type="positive")

        # Refresh after each file upload
        # self.on_refresh()
