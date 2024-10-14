import logging
from pathlib import Path

import requests
from app.modules.config import Config
from app.modules.login import check_login
from app.modules.ui_elements import create_header
from app.modules.utils import is_base64, is_hex_shellcode
from nicegui import ui

logger = logging.getLogger(__name__)


class BinaryBuilderPage:
    def __init__(self):
        self.targets = {}
        self.binaries = {}
        self.selected_payload_type = None
        self.selected_payload_name = None
        self.selected_delivery_method = None
        self.selected_delivery_name = None
        self.payload_data = {}
        self.delivery_data = {}
        # self.init_data()
        self.init_ui()

    def get_data(self):
        self.targets = self.get_targets()
        self.binaries = self.get_binaries()
        self.process_targets()

    def get_targets(self) -> dict:
        """
        Retrieve container data from the server.
        """
        try:
            url = Config().get_url() / "binary-builder" / "targets"
            token = Config().get_token()
            headers = {"Authorization": f"Bearer {token}"}

            logger.debug("Getting targets from server")
            response = requests.get(
                url, headers=headers, verify=Config().get_verify_certs()
            )

            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Targets retrieved: {data}")
                return data
            else:
                logger.warning(f"Received {response.status_code} when requesting {url}")
                return {}
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise e

    def get_binaries(self) -> dict:
        """
        Retrieve binaries data from the server.
        """
        try:
            url = Config().get_url() / "binary-builder" / "binaries"
            token = Config().get_token()
            headers = {"Authorization": f"Bearer {token}"}

            logger.debug("Getting binaries from server")
            response = requests.get(
                url, headers=headers, verify=Config().get_verify_certs()
            )

            if response.status_code == 200:
                data = response.json().get("data", {})
                logger.debug(f"Binaries retrieved: {data}")
                return data
            else:
                logger.warning(f"Received {response.status_code} when requesting {url}")
                return {}
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise e

    def process_targets(self):
        """
        Process the targets data to extract payloads and deliveries.
        """
        data = self.targets.get("data", {})
        self.payload_data = data.get("payloads", {})
        self.delivery_data = data.get("delivery", {})

    def download_binary(self, filename):
        """
        Download a binary from the server and serve it via NiceGUI.
        """
        try:
            url = str(Config().get_url() / "binary-builder" / "binaries" / filename)
            token = Config().get_token()
            headers = {"Authorization": f"Bearer {token}"}

            response = requests.get(
                url, headers=headers, stream=True, verify=Config().get_verify_certs()
            )
            if response.status_code != 200:
                ui.notify(
                    f"Failed to download {filename}: {response.status_code}",
                    type="negative",
                )
                logger.error(f"Failed to download {filename}: {response.status_code}")
                return

            temp_dir = Path("temp_download")
            temp_dir.mkdir(parents=True, exist_ok=True)
            file_path = temp_dir / filename
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            ui.download(str(file_path), filename=filename)
            ui.notify(f"Downloading {filename}...")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            ui.notify(f"An error occurred: {e}", type="negative")
            raise e

    def queue_compilation(self):
        """
        Queue the compilation based on selected options.
        """
        if not self.selected_payload_type or not self.selected_payload_name:
            ui.notify("Please select a valid payload.", type="warning")
            return
        if not self.selected_delivery_method or not self.selected_delivery_name:
            ui.notify("Please select a valid delivery method.", type="warning")
            return

        data = {
            "payload_type": self.selected_payload_type,
            "payload_name": self.selected_payload_name,
            "delivery_method": self.selected_delivery_method,
            "delivery_name": self.selected_delivery_name,
            "binary_name": self.binary_name_input.value,
            "ip": self.ip_input.value,
            "port": self.port_input.value,
            "shellcode": (
                self.shellcode_input.value if self.shellcode_input.visible else None
            ),
        }

        logger.info(f"Sending:{data}")

        self.send_compilation_request(data)

    def send_compilation_request(self, data):
        """
        Send a compilation request to the server.
        """
        try:
            url = Config().get_url() / "binary-builder" / "build"
            token = Config().get_token()
            headers = {"Authorization": f"Bearer {token}"}

            response = requests.post(
                url, headers=headers, json=data, verify=Config().get_verify_certs()
            )
            if response.status_code == 200:
                ui.notify("Successfully queued for compilation")
            else:
                logger.warning(
                    f"Compilation request failed with status {response.status_code} for {url}"
                )
                ui.notify(
                    f"Failed to queue compilation: {response.status_code}",
                    type="negative",
                )
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            ui.notify(f"An error occurred: {e}", type="negative")
            raise e

    def on_payload_select(self, selected_name):
        self.selected_payload_name = selected_name

        for payload_type in ["agents", "customs"]:
            payload_dict = self.payload_data.get(payload_type, {})
            if selected_name in payload_dict:
                self.selected_payload_type = payload_type
                payload = payload_dict[selected_name]
                break
        else:
            self.selected_payload_type = None
            payload = None

        if payload:
            self.description_header.set_content(
                f"### {selected_name.replace('_', '\\_')}"
            )
            self.description_text.set_content(payload.get("description", ""))
            self.language_text.set_content(f"Language: {payload.get('language', '')}")
            if self.selected_payload_type == "customs":
                self.shellcode_input.visible = True
                self.ip_input.visible = False
                self.port_input.visible = False

            elif self.selected_payload_type == "agents":
                self.shellcode_input.visible = False
                self.ip_input.visible = True
                self.port_input.visible = True
        else:
            self.description_header.set_content("### Select a payload")
            self.description_text.set_content(
                "Select a payload from the dropdown to proceed."
            )
            self.language_text.set_content("")
            self.shellcode_input.visible = False

    def on_delivery_select(self, selected_name):
        self.selected_delivery_name = selected_name

        for delivery_method in ["droppers", "loaders"]:
            delivery_dict = self.delivery_data.get(delivery_method, {})
            if selected_name in delivery_dict:
                self.selected_delivery_method = delivery_method
                delivery = delivery_dict[selected_name]
                break
        else:
            self.selected_delivery_method = None
            delivery = None

        if delivery:
            self.delivery_description_header.set_content(
                f"### {selected_name.replace('_', '\\_')}"
            )
            self.delivery_description_text.set_content(delivery.get("description", ""))
            self.delivery_language_text.set_content(
                f"Language: {delivery.get('language', '')}"
            )
        else:
            self.delivery_description_header.set_content("### Select a delivery method")
            self.delivery_description_text.set_content(
                "Select a delivery method from the dropdown to proceed."
            )
            self.delivery_language_text.set_content("")

    def validate_shellcode(self, hex_shellcode):
        if not is_hex_shellcode(hex_shellcode):
            ui.notify("Shellcode is not valid hex!", type="warning")

    def init_ui(self):
        @ui.page("/binary-builder")
        def binary_builder_page():
            try:
                if not check_login():
                    return

                create_header()

                # DO NOT CALL until logged in, as the login function sets the url & stuff
                self.get_data()

                with ui.tabs().classes("w-full") as tabs:
                    one = ui.tab("Options")
                    two = ui.tab("Advanced Options")

                with ui.row().classes("w-full h-[85vh] flex"):
                    with ui.card().classes("flex-1 h-full flex flex-col"):
                        ui.markdown("## Binary Builder")
                        ui.separator()

                        with ui.tab_panels(tabs, value=one).classes("w-full"):
                            with ui.tab_panel(one):
                                ## Binary Type
                                with ui.row().classes("w-full"):
                                    self.description_header = ui.markdown(
                                        "### Select a binary type"
                                    )
                                    # put the dropdown on the right
                                    ui.space()
                                    payload_options = []
                                    for payload_type in ["agents", "customs"]:
                                        payload_dict = self.payload_data.get(
                                            payload_type, {}
                                        )
                                        payload_options.extend(payload_dict.keys())

                                    self.payload_select = ui.select(
                                        payload_options,
                                        with_input=True,
                                        value=None,
                                        label="Select a binary type",
                                        on_change=lambda e: self.on_payload_select(
                                            e.value
                                        ),
                                    )

                                ui.markdown("#### Info N Stuff: ")
                                self.description_text = ui.markdown(
                                    "Select a binary type from the dropdown to proceed."
                                )

                                self.language_text = ui.markdown("Language: ...")

                                ui.separator()

                                ui.markdown("### Required options:")
                                with ui.row().classes("space-x-4"):
                                    self.ip_input = ui.input(
                                        "IP Address", placeholder="Enter IP address"
                                    )
                                    self.port_input = ui.input(
                                        "Port", placeholder="Enter port"
                                    )
                                    self.binary_name_input = ui.input(
                                        "Binary Name", placeholder="Enter binary name"
                                    )

                                self.shellcode_input = (
                                    ui.textarea(
                                        label="Shellcode (Hex)",
                                        placeholder="0x00, 0x01, etc",
                                        on_change=lambda e: self.validate_shellcode(
                                            e.value
                                        ),
                                    )
                                    .classes("w-full")
                                    .style("max-height: 400px; overflow-y: auto;")
                                    .props("clearable")
                                )
                                self.shellcode_input.visible = False

                            with ui.tab_panel(two):
                                ui.markdown("## Loader/Dropper options")

                                ## Advanced Options
                                with ui.row().classes("w-full"):

                                    # put the dropdown on the right
                                    # ui.space()

                                    self.delivery_description_header = ui.markdown(
                                        "### Select a delivery method"
                                    )

                                    ui.space()

                                    delivery_options = []
                                    for delivery_method in ["droppers", "loaders"]:
                                        delivery_dict = self.delivery_data.get(
                                            delivery_method, {}
                                        )
                                        delivery_options.extend(delivery_dict.keys())

                                    # Give this a default option
                                    self.delivery_select = ui.select(
                                        delivery_options,
                                        with_input=True,
                                        value=None,
                                        label="Select a delivery method",
                                        on_change=lambda e: self.on_delivery_select(
                                            e.value
                                        ),
                                    )

                                self.delivery_description_text = ui.markdown(
                                    "Select a delivery method from the dropdown to proceed."
                                )
                                self.delivery_language_text = ui.markdown(
                                    "Language: ..."
                                )

                                ui.separator()

                                ## Placeholder chekcbox
                                ui.markdown("## Additional Options")

                                checkbox_01 = ui.checkbox("Add in random bullshit")
                                checkbox_02 = ui.checkbox("Some Option")
                                # checkbox_03 = ui.checkbox("Some Option")
                                # checkbox_04 = ui.checkbox("Some Option")

                                ui.button(
                                    "Queue for compilation",
                                    on_click=self.queue_compilation,
                                )

                    with ui.card().classes("w-[25%] h-full flex flex-col"):
                        with ui.scroll_area().classes("h-full"):
                            ui.markdown("## Available Binaries")

                            for binary_name, _ in self.binaries.items():
                                with ui.row().classes(
                                    "justify-between items-center w-full"
                                ):
                                    ui.label(binary_name)
                                    ui.button(
                                        "Download",
                                        on_click=lambda name=binary_name: self.download_binary(
                                            name
                                        ),
                                    ).classes("ml-2")
            except Exception as e:
                logger.error(e)
                ui.notify(f"An error occurred: {e}", type="negative")


# Instantiate the page
binary_builder_page = BinaryBuilderPage()
