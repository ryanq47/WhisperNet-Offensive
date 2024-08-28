from nicegui import ui

from app.modules.log import log
from app.modules.ui_elements import create_header
from app.modules.form_j import FormJ, PowershellSync
from app.modules.config import Config
import requests
from app.modules.key_constructor import CommandParser

logger = log(__name__)

class CommandConsole:
    def __init__(self, client_id):
        self.client_id = client_id
        self.command_outputs = []
        self.timers = {}  # Dictionary to store timers for each response check

        logger.debug(f"Creating new CommandConsole for {client_id}")

        try:
            with ui.column().classes('w-full bg-gray-700 text-white').style('height: 96vh; overflow: hidden;'):

                # Header or navbar area at the top
                with ui.row().classes('w-full bg-gray-800 p-2 items-center justify-between'):
                    ui.label(f'Command Console - Client ID: {self.client_id}').classes('text-lg text-white')
                    ui.label('Status: Connected').classes('text-sm text-green-400')
                    
                    # Button to navigate back to the /clients page
                    ui.button('Back to Clients', on_click=lambda: ui.open('/clients')).classes(
                        'bg-blue-500 text-white px-4 py-1 rounded-sm'
                    )

                # Scrollable output area for displaying command outputs
                self.output_area = ui.scroll_area().classes('flex-grow p-4 space-y-4 overflow-y-auto').style(
                    'max-height: calc(100vh - 50px);'  # Dynamic height to prevent overall window scrolling
                )

                # Footer area remains at the bottom
                with ui.row().classes('w-full bg-gray-800 p-2 items-center'):
                    self.command_input = ui.input(placeholder='Enter command...').classes(
                        'flex-grow bg-gray-700 text-white px-2 py-1 rounded-sm'
                    ).style('min-width: 0;').props('autofocus')  # Allow input to shrink properly
                    
                    self.run_button = ui.button('Run', on_click=self.on_run_click).classes(
                        'bg-blue-500 text-white ml-2 px-4 py-1 rounded-sm'
                    )
                    
                    self.command_input.on('keydown.enter', lambda _: self.on_run_click())

        except requests.HTTPError as he:
            logger.error(he)
            ui.notify("An HTTP Error occured - check logs")

        except Exception as e:
            logger.error(e)
            ui.notify("An unknown error occured - check logs")

    def on_run_click(self):
        """Handles the run button click or Enter key press to execute command."""
        try:
            command = self.command_input.value.strip()
            if command:
                self.command_input.value = ''  # Clear the input field - needs to go first
                self.execute_command(command)  # then execute the command

        except Exception as e:
            logger.error(e)
            raise e

    def execute_command(self, command):
        """Executes the given command and checks for a response."""
        
        try:
            # Placeholder for actual command execution logic
            output = f"> {command}"

            constructed_key = CommandParser().parse_command(command)
            # Generate formJ message, with sync keys
            form_j_message = FormJ.generate(data=constructed_key)

            # get RID from that message
            rid = form_j_message.get("rid")

            if rid is None:
                ui.notify("RID is none - this is bad, cannot track message")

            # construct URL to post command to
            post_url = Config().get_url() / "command" / self.client_id
            logger.debug(f"Posting command to {post_url}")

            # Send to correct endpoint to queue message
            headers = {'Authorization': f'Bearer {Config().get_token()}'}
            
            # send to server and handle response
            response = requests.post(post_url, json=form_j_message, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Got {response.status_code} from server.")
                raise requests.HTTPError(
                    f"Got {response.status_code} from server: {response.text}"
                )
            
            # if 200, start waiting for response            
            # Start the timer for this specific response check
            self.timers[rid] = ui.timer(interval=2, callback=lambda: self.check_response(rid))
            
            # Display command that is run out to screen
            self.command_outputs.append(output)
            self.display_output(output)
        
        except Exception as e:
            logger.error(f"Error executing command: {e}")

    # need sep fucnc for timer to work properly
    def check_response(self, rid):
        """Checks for a response from the endpoint."""
        try:
            # moved response url into this func
            response_url = Config().get_url() / "response" / rid
            logger.debug(f"checking for response at {response_url}")

            headers = {'Authorization': f'Bearer {Config().get_token()}'}

            response = requests.get(response_url, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                # convert message to formj
                form_j_message = FormJ(response_data).parse()

                #self.display_output(response_data['data'])
                # need to stringify it
                # for now, just displaying the rid
                self.display_output(str(form_j_message.rid))

                # Stop the timer as we've received a valid response
                if rid in self.timers:
                    self.timers[rid].cancel()
                    del self.timers[rid]
                
            if response.status_code == 401:
                logger.info("Server says missing creds, status code: 401")
                ui.notify("Server says missing creds, status code: 401")
            else:
                logger.info(f"Waiting for response... Status: {response.status_code}")
                ui.notify("waiting on valid response...")

        except requests.RequestException as e:
            ui.notify("Error occured - Check Logs")
            logger.error(f"Error checking response: {e}")
        
    def display_output(self, output):
        """Displays the output in the output area and scrolls to the latest message."""
        try:
            # Append output to the output area
            with self.output_area:
                ui.label(output).classes('text-sm text-white').style('white-space: pre-wrap;')
            #self.scroll_to_bottom()

        except Exception as e:
            logger.error(e)
            raise e

    # ALSO BROKEN
    def scroll_to_bottom(self):
        """Scrolls the output area to the bottom to show the latest message. - not working"""
        try:
            pass
            #self.output_area.run_method('scrollTo', {'top': self.output_area.element['scrollHeight']})

        except Exception as e:
            logger.error(e)
            raise e
