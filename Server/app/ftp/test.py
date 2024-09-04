from nicegui import app, ui

app.add_static_files('/examples', 'examples')
#ui.label('Some NiceGUI Examples').classes('text-h5')
#ui.link('AI interface', '/examples/ai_interface/main.py')
#ui.link('Custom FastAPI app', '/examples/fastapi/main.py')
#ui.link('Authentication', '/examples/authentication/main.py')

ui.run()
