import argparse
from nicegui import ui, app
from app.startup import startup
from app.modules.config import Config
from app.modules.log import log

# Set up logger
logger = log(__name__)

# Argument parsing setup with help
parser = argparse.ArgumentParser(description="Run the NiceGUI app with optional host and port settings.")
parser.add_argument(
    "--host", 
    type=str, 
    default="127.0.0.1", 
    help="The host IP address to run the app on. Default is '127.0.0.1'."
)
parser.add_argument(
    "--port", 
    type=int, 
    default=8080, 
    help="The port number to run the app on. Default is 8080."
)
args = parser.parse_args()

# Setup config
logger.debug("Initializing Config")
Config()

# Serve static files
app.add_static_files('/static', 'static')

# Startup tasks
logger.debug("Starting app")
app.on_startup(startup)

# Run NiceGUI app with argparse host and port
ui.run(
    dark=True,
    host=args.host,
    port=args.port,
    favicon="static/icon.png",
    title="Whispernet-Offensive"
)

# image: https://pngtree.com/freepng/cyber-hacker-icon_6566749.html