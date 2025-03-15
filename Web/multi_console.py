from nicegui import ui, app
import asyncio
import requests
from cards import agent_card, unknown_card
from config import Config, ThemeConfig
from build import BuildView
from navbar import *
from networking import api_call, api_post_call, api_delete_call
from scripts import ScriptsView
from nicegui.events import KeyEventArguments
from agent import AgentsView, AgentView


class MultiConsolePage:
    """
    Multi console for interacting with multiple agents
    """

    def __init__(self, agent_id: str = None): ...

    def render(self):
        """
        Renders the complete agent view including header, tabs, and tab panels.
        """
        with ui.element().classes("w-full h-full"):

            current_settings = app.storage.user.get("settings", {})

            with ui.splitter().classes("h-full") as splitter:
                with splitter.before:
                    # maybe get a custom one in here with a select option?
                    AgentsView().render()
                    # ui.label("Agents Aggrid")
                with splitter.after:
                    # custom console here too
                    self.render_shell()

    def render_shell(self):
        """
        Renders the SHELL tab with a scrollable command history and an input area.
        Auto-refresh occurs every second.
        """
        # Enable auto-scroll when near the bottom.
        self.auto_scroll_enabled = True
        # Keep track of which command entries have been appended.
        self.known_command_ids = {}

        # and finally, render the script options
        # self.render_scripts_options()

        def handle_keydown(e):
            # Trigger send_command on Enter key.
            if e.args.get("key") == "Enter":
                send_command()

        # fix: get current script. If current script is none, put "no script selected" on selector.
        # additionally, break it out a bit, it's annoyingly duct taped together

        def on_scroll(e):
            # If the user scrolls away from the bottom, disable auto-scroll.
            self.auto_scroll_enabled = e.vertical_percentage >= 0.95

        def update_shell_data():
            # instead of none, get something here, maybe all the responses? or don't even bother with shell result history?
            data = None  # api_call(url=f"/agent/{self.agent_id}/command/all").get("data", [])
            if not data:
                return

            # Sort entries chronologically.
            data.sort(key=lambda entry: entry.get("timestamp", ""))
            for entry in data:
                # Use a unique identifier for the command.
                cmd_id = entry.get("command_id", "")
                if not cmd_id:
                    cmd_id = f"no_id_{entry.get('timestamp', '')}"
                cmd = entry.get("command", "")
                response_value = entry.get("response") or "Waiting on callback..."

                if cmd_id not in self.known_command_ids:
                    # Append new entry HTML to the output element.
                    html = (
                        f"<div id='shell_entry_{cmd_id}' style='margin-bottom: 10px;'>"
                        f"<div style='font-family: monospace;'>&gt; {cmd}</div>"
                        f"<div id='response_{cmd_id}' style='white-space: pre; font-family: monospace;'>{response_value}</div>"
                        "<hr/></div>"
                    )
                    ui.run_javascript(
                        f"document.getElementById('shell_output').insertAdjacentHTML('beforeend', {html!r});"
                    )
                    self.known_command_ids[cmd_id] = True
                else:
                    # Update an existing entry's response only if new response data is available.
                    if response_value:
                        # Update using only text node modification if no selection is active.
                        js_code = f"""
    (function() {{
    var selection = window.getSelection();
    if (!selection || selection.toString() === "") {{
        var elem = document.getElementById('response_{cmd_id}');
        if (elem && elem.firstChild) {{
        elem.firstChild.nodeValue = {response_value!r};
        }}
    }}
    }})();
    """
                        ui.run_javascript(js_code)
            # Auto-scroll if enabled.
            if self.auto_scroll_enabled:
                ui.run_javascript(
                    """
                    var el = document.getElementById('shell_output');
                    el.scrollTop = el.scrollHeight;
                """
                )

        def send_command():
            # api_post_call(
            #     url=f"/agent/{self.agent_id}/command/enqueue",
            #     data={"command": command_input.value},
            # )
            command_input.value = ""
            update_shell_data()

        # Initialize the script options.
        # render_scripts_options()
        # on load, load "default.py", the default scirpt
        # ducttape bug fix, if this is not called, no script is rendered, and if there's only one script, you can't select a script
        # update_script("default.py")
        # FUCK this doesn't work, script forces default.py on refresh...

        # Shell tab layout.
        with ui.column().classes("h-full w-full flex flex-col"):
            # Command History Area.
            with ui.row().classes("grow w-full p-4"):
                with ui.scroll_area(on_scroll=on_scroll).classes(
                    "w-full h-full border rounded-lg p-2"
                ):
                    # Create a single HTML element to hold the shell output.
                    ui.html(
                        "<div id='shell_output' style='white-space: pre-wrap; font-family: monospace;'>Shell Output:</div>"
                    )
            # Command Input Area.
            with ui.row().classes("w-full items-center p-4"):
                command_input = (
                    ui.textarea(placeholder="Type a command...")
                    .props('autofocus outlined input-class="ml-3" input-class="h-12"')
                    .classes("text-black grow mr-4")
                    .on("keydown", handle_keydown)
                )
                ui.button("Send Command", on_click=send_command).classes("w-32")

        # Load the initial shell data and set up the auto-refresh timer.
        update_shell_data()
        ui.timer(interval=1.0, callback=update_shell_data)

    ## update me with selection of all scripts - need to think the scritps through
    # def render_scripts_options(self):
    #     """
    #     Handles the script options.

    #     Checks if an agent has a script. If so, sets that to the current script on the ui.select
    #     If not, display's None.

    #     When updating a script, it calls the _register_script to update the script for the agent.

    #     """
    #     # Get the list of available scripts.
    #     response = api_call(url="/scripts/files")
    #     scripts_data = (
    #         [
    #             script.get("filename", "Unknown Script")
    #             for script in response.get("data", [])
    #         ]
    #         if response.get("data")
    #         else ["No Scripts Available"]
    #     )

    #     # with agent id, get current script.
    #     agent_data = api_call(url=f"/stats/agent/{self.agent_id}").get("data", {})

    #     # Get the inner dictionary, which holds the actual agent info. Only one agent is returned from this call, so it'll just grab the first one
    #     agent_info = next(iter(agent_data.values()), {})

    #     # Then navigate to the command_script inside the nested structure.
    #     agent_script = (
    #         agent_info.get("data", {}).get("config", {}).get("command_script")
    #     )

    #     # Create the script selector dropdown.
    #     ui.select(
    #         options=scripts_data,
    #         label="Extension Scripts",
    #         on_change=lambda e: self._register_script(e.value),
    #         value=agent_script,  # show the currently selected script if there is one
    #     ).classes("w-full")

    # def _register_script(self, script_name):
    #     """
    #     POST call to update the script for an agent on the server

    #     script_name: The name of the script on the server

    #     Usually this would be under the render_scripts_options method, but ui.select needs a callback func to call on change

    #     Endpoint: /agent/{self.agent_id}/command-script/register

    #     """
    #     api_post_call(
    #         url=f"/agent/{self.agent_id}/command-script/register",
    #         data={"command_script": script_name},
    #     )
    #     ui.notify(f"Updated script to {script_name} on agent", position="top-right")
