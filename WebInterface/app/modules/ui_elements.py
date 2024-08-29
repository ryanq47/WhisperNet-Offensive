from nicegui import ui
from app.modules.config import Config

# Creates a navbar
def create_header():
    with ui.header() as header:
        with ui.row().classes('w-full justify-between').style("background-color:"):  # Full width and space between elements
            # Left-aligned items
            with ui.row():
                ui.label('WhisperNet-Offensive').classes('text-h6')
                ui.button('Home', on_click=lambda: ui.open('/home'), color=Config().get_button_color())
                ui.button('Clients', on_click=lambda: ui.open('/clients'), color=Config().get_button_color())
            
            # Right-aligned item
            ui.button('Log Out', on_click=lambda: ui.open('/logout'), color=Config().get_button_color())


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