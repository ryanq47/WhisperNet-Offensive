from nicegui import ui
import httpx  # For making HTTP requests
from app.modules.config import Config
from app.modules.log import log
import re

logger = log(__name__)

# Store session data - toss this in a singleton maybe?
session_store = {}

@ui.page('/login')
def login_page():
    """
    A basic login page with centered elements.
    """
    def is_valid_url(url):
        # Regular expression for validating a URL
        regex = re.compile(
            r'^(https?|ftp)://'  # Protocol: http, https, or ftp
            r'(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}|'  # Domain name (e.g., example.com)
            r'localhost|'  # Localhost
            r'(\d{1,3}\.){3}\d{1,3}|'  # IPv4 (e.g., 192.168.0.1)
            r'\[?[a-fA-F0-9:]+\]?)'  # IPv6 (e.g., [2001:db8::1])
            r'(:\d{1,5})?'  # Optional port (e.g., :8080)
            r'(/.*)?$'  # Path (e.g., /path/to/resource)
        )
        return re.match(regex, url) is not None

    def validate_and_set_url(url):
        if is_valid_url(url):
            Config().set_url(url)
            ui.notify('Server URL set successfully.', type='positive')
        else:
            ui.notify('Invalid URL. Please enter a valid server URL.', type='negative')

    # Use a column layout inside a card to center all the elements in the middle of the screen
    with ui.column().classes('justify-center items-center h-screen w-screen'):
        with ui.card().classes('p-8'):
            # Title centered
            ui.markdown('## Whispernet-Offensive Login').classes('text-center mb-4')

            # Server input with autofocus and validation on blur
            server_input = ui.input('Server').props('autofocus').on(
                'blur', lambda: validate_and_set_url(server_input.value)
            )

            # Username input with autofocus starting cursor there
            username_input = ui.input('Username').props('autofocus').on(
                'blur', lambda: Config().set_credentials(username_input.value, Config().password)
            )

            # Password input, with the Enter key triggering the login function
            password_input = ui.input('Password', password=True).props('autofocus').on(
                'blur', lambda: Config().set_credentials(Config().username, password_input.value)
            ).on(
                'keydown.enter', lambda e: login(username_input.value, password_input.value)
            )

            # Login button to submit credentials
            ui.button('Login', on_click=lambda: login(username_input.value, password_input.value))

def login_required(page_func):
    """Decorator to ensure user is logged in before accessing the page."""
    def wrapper():
        if 'logged_in' in session_store and session_store['logged_in']:
            return page_func()  # Call the original page function
        else:
            ui.notify('You must log in to access this page.', type='warning')
            ui.open('/login')
    return wrapper

def main_page():
    """Main page that requires login."""
    try:
        if 'logged_in' in session_store and session_store['logged_in']:
            ui.label('Welcome to the main page!')
        else:
            ui.notify('You must log in to access this page.', type='warning')
            ui.open('/login')

    except Exception as e:
        logger.error(e)
        raise e

async def login(username, password):
    """Authenticate user via API and set session."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(str(Config().url / 'login'), json={'username': username, 'password': password})
            
            # not redirectiong, maybe add session? need to check if that's needed
            if response.status_code == 200:
                Config().set_token(response.json().get('data',{}).get('token'))
                session_store['logged_in'] = True
                logger.info(f"User {username} logged in")
                ui.open('/clients')  # Navigate to the clients page after successful login
            else:
                ui.notify('Invalid credentials', type='negative')

    except Exception as e:
        logger.error(e)
        #ui.notify("An unkown error occured")
        raise e