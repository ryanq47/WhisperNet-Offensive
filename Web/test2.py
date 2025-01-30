from nicegui import ui

# Remove default padding/margin from the page
ui.add_head_html('<style>html, body { margin: 0; padding: 0; }</style>')

# Define the main layout
ui.header().classes('border h-12 bg-gray-800 text-white flex items-center justify-between px-4')
with ui.element().classes('h-full border flex-1 bg-gray-100 flex items-center justify-center overflow-hidden'):
    ui.label('Main Content').classes('border text-xl')

ui.run()
