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


# ---------------------------
#   FileView Class
# ---------------------------
class FileView:
    """
    Displays a page for managing files in the static-serve plugin,
    with multi-file upload, multi-row selection, and 'Delete Selected'.
    """

    def __init__(self):
        self.file_list = []
        self.aggrid_element = None

    def fetch_file_list(self):
        """
        Calls GET /static-serve/files to get the list of files.
        Expects JSON like:
        {
          "status": 200,
          "data": [
            { "filename": "file1.txt", "filehash": "...", "filepath": "/static/file1.txt" },
            ...
          ],
          "message": "..."
        }
        """
        resp = api_call("static-serve/files")
        self.file_list = resp.get("data", [])

    def on_refresh(self):
        """
        Refresh the grid with the latest file list.
        """
        self.fetch_file_list()
        self.update_aggrid()

    def update_aggrid(self):
        """
        Convert self.file_list -> row data for AG Grid.
        We'll store both 'FilenameLink' for display (HTML)
        and 'FilenameRaw' for actual deletion reference.
        """
        row_data = []
        for f in self.file_list:
            raw_name = f.get("filename", "")
            filehash = f.get("filehash", "")
            web_path = f.get("filepath", "")  # e.g. "/static/file.exe"

            # Create clickable link for direct download
            clickable_link = f"<a href='{web_path}' target='_blank'>{raw_name}</a>"

            # We'll store the raw filename in a separate field for deletion
            row_data.append(
                {
                    "FilenameLink": clickable_link,
                    "FilenameRaw": raw_name,
                    "Hash": filehash,
                    "WebPath": web_path,
                }
            )

        self.aggrid_element.options["rowData"] = row_data
        self.aggrid_element.update()

    def on_file_upload(self, upload_result):
        """
        Called for each file if multiple=True.
        We'll send it to POST /static-serve/upload as multipart/form-data.
        """
        files = {
            "file": (upload_result.name, upload_result.content),
        }
        # If you want to rename server-side, pass "filename" in data
        data = {}
        resp = api_post_call("static-serve/upload", data=data, files=files)
        if not resp or resp.get("status") != 200:
            ui.notify(
                f"Upload failed: {resp.get('message', 'Unknown error')}",
                type="negative",
            )
        else:
            ui.notify("File uploaded successfully!", type="positive")

        # Optionally refresh after each file upload:
        self.on_refresh()

    def render(self):
        """
        Renders the NiceGUI page:
         - Title/Labels
         - 'Refresh' + 'Delete Selected' + 'Upload' controls
         - AG Grid with checkboxes
        """
        with ui.column().classes("w-full h-full space-y-4"):
            ui.label(
                "*REMEMBER*, everything hosted here can be accessed by anyone who can reach the server."
            )
            ui.label("Static Serve Plugin").classes("text-3xl")

            # Buttons row
            with ui.row().classes("gap-4"):
                ui.button("Refresh", on_click=self.on_refresh).props("outline")
                ui.button(
                    "Delete Selected - BROKEN", on_click=...  # self.on_delete_selected
                ).props("outline")

                ui.upload(
                    label="Upload File(s)",
                    on_upload=self.on_file_upload,
                    auto_upload=True,
                    multiple=True,  # allow selecting multiple files at once
                )

            # Setup AG Grid
            current_settings = app.storage.user.get("settings", {})
            aggrid_theme = (
                "ag-theme-balham-dark"
                if current_settings.get("Dark Mode", False)
                else "ag-theme-balham"
            )

            self.aggrid_element = (
                ui.aggrid(
                    {
                        # Let AG Grid automatically adjust height
                        "domLayout": "autoHeight",
                        "columnDefs": [
                            # Checkbox selection column
                            {
                                "headerName": "",
                                "checkboxSelection": True,
                                "headerCheckboxSelection": True,
                                "width": 50,
                                "pinned": "left",
                            },
                            {
                                "headerName": "Filename",
                                "field": "FilenameLink",
                                "cellRenderer": "htmlCellRenderer",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 250,
                            },
                            {
                                "headerName": "Hash",
                                "field": "Hash",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 240,
                            },
                            {
                                "headerName": "Web Path",
                                "field": "WebPath",
                                "cellRenderer": "htmlCellRenderer",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "width": 300,
                            },
                        ],
                        # Enable multiple row selection
                        "rowSelection": "multiple",
                        "rowData": [],
                    },
                )
                .classes(f"{aggrid_theme} w-full")
                .style("height: 600px")
            )

        # Initial load
        self.on_refresh()
