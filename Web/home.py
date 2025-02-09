from nicegui import ui
from searchbar import Search
from networking import api_call, api_post_call, api_delete_call
from config import Config, ThemeConfig


class HomeView:
    def __init__(self):
        pass

    @ui.page("/")
    def render(self):
        try:

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
                        agent_data = api_call(url=f"{Config.API_HOST}/stats/agents")
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
                        listener_data = api_call(
                            url=f"{Config.API_HOST}/stats/listeners"
                        )
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

                # figure out later, needs a bit of adjustment
                # # Searchbar Section
                # with ui.row().classes(
                #     "w-full items-center justify-center mt-6"
                # ):
                #     ui.label("Searchbar").classes(
                #         "text-lg  600 font-medium mb-2 underline"
                #     )
                #     s = Search(
                #         vertical_padding=False, full_horizontal_width=True
                #     )
                #     s.spawn_search_bar()

        except Exception as e:
            print(e)
            raise e
