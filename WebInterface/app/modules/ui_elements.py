from nicegui import ui
from app.modules.config import Config

# Creates a navbar
def create_header():
    with ui.header().classes("m-0 p-0") as header:  # Remove any margin or padding from header
        with ui.row().classes('w-full justify-between items-center m-0 p-0').style(f"background-color: {Config().get_button_color()};"):  # Full width, space between elements, no margin/padding, and centered items
            
            # Left-aligned text (not in a button)
            ui.label('WhisperNet-Offensive').classes('text-h6 m-0 p-0')

            # Right-aligned items (buttons in a row without spacing)
            with ui.row().classes("m-0 p-0 gap-0 items-center"):  # No margin/padding and no gap between buttons
                ui.button('Home', on_click=lambda: ui.open('/home'), color=Config().get_button_color()).classes("m-0 p-0 rounded-none w-24")  # Remove rounded corners, fixed width
                ui.button('Clients', on_click=lambda: ui.open('/clients'), color=Config().get_button_color()).classes("m-0 p-0 rounded-none w-24")
                ui.button('Log Out', on_click=lambda: ui.open('/logout'), color=Config().get_button_color()).classes("m-0 p-0 rounded-none w-24")


"""
def add_particles_background():
    # Add the particles.js container and reference the scripts from the static directory
    ui.add_body_html('''
    <div id="particles-js" style="position: fixed; width: 100%; height: 100%; z-index: -1;"></div>
    <script src="/static/particles.js"></script>
    <script>
        particlesJS.load('particles-js', '/static/particlesjs-config.json', function() {
            console.log('particles.js loaded - callback');
        });
    </script>
    ''')
"""

def add_particles_background():
    # Add the particles.js container and load the existing configuration
    ui.add_body_html('''
    <div id="particles-js" style="position: fixed; width: 100%; height: 100%; z-index: -1;"></div>
    <script src="/static/particles.js"></script>
    <script>
        // Load particles.js with your existing configuration
        particlesJS.load('particles-js', '/static/particlesjs-config.json', function() {
            console.log('particles.js loaded - callback');
        });
    </script>
    ''')