from nicegui import ui
import requests
import httpx
from app.modules.log import log

logger = log(__name__)

from yarl import URL

class CommandConsole:
    def __init__(self, client_id):
        self.client_id = client_id
        self.command_outputs = []
        #self.base_url - set this up in a config or something
        #self.command_endpoint = Config().base_url / client_type / client-id
        
        logger.debug(f"Creating new CommandConsole for {client_id}")
        # Set up the main layout for the console
        with ui.column().classes('h-screen w-full bg-gray-900 text-white'):
            
            # Scrollable output area
            with ui.column().classes('flex-1 p-4 space-y-4 overflow-y-auto') as self.output_area:
                pass  # This container will hold command outputs

            # Fixed command input area at the bottom
            with ui.row().classes('w-full bg-gray-800 p-2 fixed bottom-0 items-center'):
                ui.label("C:\\>").classes('text-white')
                self.command_input = ui.input(placeholder='Enter command here...').classes('w-full bg-gray-900 text-white')

                # Run button tied to command execution
                self.run_button = ui.button('Run', on_click=lambda: self.execute_command(self.command_input.value))
                self.run_button.classes('bg-blue-500 text-white ml-2')

                # Attach Enter key to run button
                self.command_input.on('keydown.enter', lambda _: self.execute_command(self.command_input.value))

    async def execute_command(self, command: str):
        if command.strip():
            async with httpx.AsyncClient() as client:  # Create an async client context
                try:
                    # Perform the asynchronous GET request
                    response = await client.get('https://google.com')  # Replace with your actual API

                    if response.status_code == 200:
                        output = response.text
                    else:
                        output = f"Error: {response.status_code} - {response.reason_phrase}"

                except httpx.RequestError as e:
                    output = f"Request error: {e}"

            self.command_outputs.append(output)  # Add new output to the end
            self.update_output_display()
            self.command_input.value = ''  # Clear the input after execution


    def update_output_display(self):
        self.output_area.clear()
        with self.output_area:
            for output in self.command_outputs:
                # Convert any client ID in output to a clickable link
                ui.markdown(f"[View client {self.client_id}](http://localhost:8080/client/{self.client_id})\n\n```\n{output}\n```")
        #self.output_area.scroll_to()  # Scroll to the bottom to show the most recent message
