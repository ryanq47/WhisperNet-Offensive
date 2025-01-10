#!/usr/bin/env python3

## NOTES: styling, tailwind
# Elements: Quasar. Check each docs for each thing
from nicegui import events, ui
from searchbar import Search

with ui.header().classes(replace="row items-center").classes(
    "bg-neutral-800"
) as header:
    ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props(
        "flat color=white"
    )
    with ui.tabs() as tabs:
        ui.tab("A")
        ui.tab("B")
        ui.tab("Search")

with ui.footer(value=False) as footer:
    ui.label("Footer")

with ui.left_drawer().classes("bg-neutral-600") as left_drawer:
    ui.label("Menu")

    for i in range(0, 5):
        # ui.label('SomeSection')
        ui.button(
            f"Button {i}", on_click=footer.toggle, color="bg-neutral-600"
        ).classes("w-full text-slate-50").props("square flat condensed")
        # https://quasar.dev/vue-components/button/
        ui.separator()


with ui.page_sticky(position="bottom-right", x_offset=20, y_offset=20):
    ui.button(on_click=footer.toggle, icon="contact_support").props("fab")

# Tabs are nice as you don't need to define a new header/footer
with ui.tab_panels(tabs, value="A").classes("w-full"):
    with ui.tab_panel("A"):
        ui.label("Content of A")
    with ui.tab_panel("B"):
        ui.label("Content of B")
    with ui.tab_panel("Search"):
        ui.label("Search")
        s = Search()
        s.spawn_search_bar()


ui.run()
