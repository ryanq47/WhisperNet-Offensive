from nicegui import ui, app
from app.startup import startup
from app.modules.config import Config
from app.modules.log import log

logger = log(__name__)

# setup config
logger.debug("Initializing Config")
Config()

app.add_static_files('/static', 'static')

logger.debug("Starting app")
app.on_startup(startup)



ui.run(dark=True)