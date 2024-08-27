from nicegui import ui

from app.modules.log import log
from app.modules.ui_elements import create_header
from app.modules.form_j import FormJ, PowershellSync
from app.modules.config import Config
import requests

logger = log(__name__)

class CommandConsole:
    def __init__(self, client_id):
        self.client_id = client_id
        self.command_outputs = []
        self.timers = {}  # Dictionary to store timers for each response check

        logger.debug(f"Creating new CommandConsole for {client_id}")

        #create_header()
        # Main container with a height of 100vh to prevent scrolling
        #with ui.column().classes('w-full h-full bg-gray-900 text-white').style('overflow: hidden;'):
        # need to set height to 96, as 100 is for some reason too big & creates a scroll bar
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
                self.execute_command(command)

        except Exception as e:
            logger.error(e)
            raise e

    def execute_command(self, command):
        """Executes the given command and checks for a response."""
        
        try:
            # Placeholder for actual command execution logic
            output = f"Placeholder - Executed command: {command}"
            
            # Split command into parts
            command_head = command.split()[0]
            command_tail = ' '.join(command.split()[1:])
            
            # Placeholder for real logic based on input
            powershell_key = PowershellSync(command=command_head).create()
            
            # Generate keys with command_head
            form_j_message = FormJ.generate(data=powershell_key)
            rid = form_j_message.get("rid")

            if rid is None:
                ui.notify("rid is None - Bad")

            post_url = Config().get_url() / "command" / self.client_id
            print(f"posting command to: {post_url}")
            
            # Send to correct endpoint to queue message
            token = Config().get_token()
            headers = {'Authorization': f'Bearer {token}'}
            
            response = requests.post(post_url, json=form_j_message, headers=headers)
            if response.status_code != 200:
                logger.error(f"Got {response.status_code} from server.")
                raise requests.HTTPError(
                    f"Got {response.status_code} from server: {response.text}"
                )
            
            response_url = Config().get_url() / "response" / rid
            print(f"RID: {rid}")
            
            # Start the timer for this specific response check
            self.timers[rid] = ui.timer(interval=2, callback=lambda: self.check_response(response_url, rid))
            
            # Display output back
            self.command_outputs.append(output)
            self.display_output(output)
        
        except Exception as e:
            logger.error(f"Error executing command: {e}")

    def check_response(self, endpoint_url, rid):
        """Checks for a response from the endpoint."""
        print(f"CHECKING FOR RESPONSE AT {endpoint_url}")
        try:
            headers = {'Authorization': f'Bearer {Config().get_token()}'}

            response = requests.get(endpoint_url, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                ui.notify(response_data)
                self.display_output(response_data['data'])
                
                # Stop the timer as we've received a valid response
                if rid in self.timers:
                    self.timers[rid].cancel()
                    del self.timers[rid]
                
                return False  # Stop checking further

            if response.status_code == 401:
                logger.info("Server says missing creds, status code: 401")
                ui.notify("Server says missing creds, status code: 401")
            else:
                logger.info(f"Waiting for response... Status: {response.status_code}")
                ui.notify("waiting on valid response...")
        except requests.RequestException as e:
            logger.error(f"Error checking response: {e}")
        
        return True  # Continue the timer to keep checking
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

    def scroll_to_bottom(self):
        """Scrolls the output area to the bottom to show the latest message. - not working"""
        try:
            pass
            #self.output_area.run_method('scrollTo', {'top': self.output_area.element['scrollHeight']})

        except Exception as e:
            logger.error(e)
            raise e
