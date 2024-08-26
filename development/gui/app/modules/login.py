from nicegui import ui
import httpx  # For making HTTP requests

# API endpoint for authentication
AUTH_API_URL = 'http://127.0.0.1:8081/login'

# Store session data
session_store = {}


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
    if 'logged_in' in session_store and session_store['logged_in']:
        ui.label('Welcome to the main page!')
    else:
        ui.notify('You must log in to access this page.', type='warning')
        ui.open('/login')

@ui.page('/login')
def login_page():
    """
    A basic login page with centered elements.
    """

    # Use a column layout inside a card to center all the elements in the middle of the screen
    with ui.column().classes('justify-center items-center h-screen w-screen'):
        with ui.card().classes('p-8'):
            # Title centered
            ui.markdown('## Whispernet-Offensive Login').classes('text-center mb-4')

            # Server input with autofocus
            server_input = ui.input('Server').props('autofocus')

            # Username input with autofocus starting cursor there
            username_input = ui.input('Username').props('autofocus')

            # Password input, with the Enter key triggering the login function
            password_input = ui.input('Password', password=True).props('autofocus').on(
                'keydown.enter', lambda e: login(username_input.value, password_input.value))

            # Login button to submit credentials
            ui.button('Login', on_click=lambda: login(username_input.value, password_input.value))

async def login(username, password):
    """
        Login to API
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(AUTH_API_URL, json={'username': username, 'password': password})
        
        if response.status_code == 200: #and response.json().get('authenticated'):
            session_store['logged_in'] = True
            ui.open('/')  # Navigate to the main page
        else:
            ui.notify('Invalid credentials', type='negative')