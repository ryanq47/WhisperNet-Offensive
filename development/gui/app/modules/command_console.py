from nicegui import ui

from app.modules.log import log
from app.modules.ui_elements import create_header

logger = log(__name__)

class CommandConsole:
    def __init__(self, client_id):
        self.client_id = client_id
        self.command_outputs = []

        logger.debug(f"Creating new CommandConsole for {client_id}")

        #create_header()
        # Main container with a height of 100vh to prevent scrolling
        #with ui.column().classes('w-full h-full bg-gray-900 text-white').style('overflow: hidden;'):
        # need to set height to 96, as 100 is for some reason too big & creates a scroll bar
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
        """Executes the given command and displays the output."""
    
        try:
            # Placeholder for actual command execution logic
            output = f"Placeholder - Executed command: {command}"
            # parse command into formJ

            # async send to correct endpoint to queue message

            # async check response url until there's a message back


            # display output back
            self.command_outputs.append(output)
            self.display_output(output)
        except Exception as e:
            logger.error(e)
            raise e

    def display_output(self, output):
        """Displays the output in the output area and scrolls to the latest message."""
        try:
            # Append output to the output area
            with self.output_area:
                ui.label(output).classes('text-sm text-white').style('white-space: pre-wrap;')
            self.scroll_to_bottom()

        except Exception as e:
            logger.error(e)
            raise e

    def scroll_to_bottom(self):
        """Scrolls the output area to the bottom to show the latest message."""
        try:
            self.output_area.run_method('scrollTo', {'top': self.output_area.element['scrollHeight']})

        except Exception as e:
            logger.error(e)
            raise e
