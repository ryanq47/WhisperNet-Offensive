from nicegui import ui
from networking import api_call, api_post_call, api_delete_call
from config import Config, ThemeConfig


class HomeView:
    def __init__(self):
        pass

    @ui.page("/")
    def render(self):
        try:
            self.render_help_button()
            with ui.element().classes(
                "w-1/2 absolute-center items-center justify-center"
            ):
                with ui.row().classes("items-center justify-center"):
                    # ui.icon("home").classes("text-blue-500 text-6xl")
                    ui.image("/static/icon_full.png").classes("w-32 h-32")

                    ui.label("WhisperNet Dashboard").classes(
                        "text-3xl font-bold  700 ml-4"
                    )

                    # Subheader
                    ui.label(
                        "Some really cool oneliner that explains the platform!!!!"
                    ).classes("text-lg  600 text-center leading-6")
                    ui.separator()

                # Status Section
                with ui.row().classes("w-full flex-wrap justify-between gap-4 mt-6"):
                    # Active Agents
                    with ui.column().classes(
                        "flex-1 items-center text-center p-4 bg-blue-50 rounded-md shadow-sm"
                    ):
                        agent_data = api_call(url=f"/stats/agents")
                        num_active_agents = len(agent_data.get("data", {}).keys())

                        ui.icon("computer").classes("text-blue-600 text-5xl")
                        ui.button(
                            f"{num_active_agents} Active Agents",
                            on_click=lambda nav: ui.navigate.to("/agents"),
                        ).classes("text-xl font-medium  700").props("flat")

                    # Online Listeners
                    with ui.column().classes(
                        "flex-1 items-center text-center p-4 bg-green-50 rounded-md shadow-sm"
                    ):
                        listener_data = api_call(url=f"/stats/listeners")
                        num_active_listeners = len(listener_data.get("data", {}).keys())
                        ui.icon("headphones").classes("text-green-600 text-5xl")
                        ui.button(
                            f"{num_active_listeners} Listeners Online",
                            on_click=lambda nav: ui.navigate.to("/listeners"),
                        ).classes("text-xl font-medium  700").props("flat")

                    # Alerts - can integrate later
                    # with ui.column().classes(
                    #     "flex-1 items-center text-center p-4 bg-red-50 rounded-md shadow-sm"
                    # ):
                    #     ui.icon("notifications").classes(
                    #         "text-red-600 text-5xl"
                    #     )
                    #     ui.label("2 Alerts").classes(
                    #         "text-xl font-medium  700"
                    #     )
                    ui.separator()

        except Exception as e:
            print(e)
            raise e

    async def open_help_dialog(self) -> None:
        """Open a help dialog with instructions for the shellcode converter."""
        with ui.dialog().classes("w-full").props("full-width") as dialog, ui.card():
            ui.markdown("# HomePage:")
            ui.separator()
            ui.markdown(
                """
                The home page for WhisperNet. 

                Click on "X Active Agents" to go to the agents page
                Click on "X Listeners Online" to go to the agents page

                Otherwise, navigate with either the top navbar, or the menu on the left (click the hamburger button)
                """
            )
        dialog.open()
        await dialog

    def render_help_button(self) -> None:
        """Render a help button pinned at the bottom-right of the screen."""
        help_button = ui.button("Current Page Info", on_click=self.open_help_dialog)
        help_button.style("position: fixed; top: 170px; right: 24px; ")
