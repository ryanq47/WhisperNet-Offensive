from yarl import URL
from app.modules.log import log

logger = log(__name__)

# config signleton

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            # Initialize default configuration values
            cls._instance.url = URL()
            cls._instance.username = ''
            cls._instance.password = ''
            cls._instance.current_token = None
            cls._instance.active_sessions = []
        return cls._instance

    def set_url(self, url: str):
        """Sets the URL using yarl for better URL handling."""
        logger.info(f"Setting URL: {url}")
        self.url = URL(url)

    def set_credentials(self, username: str, password: str):
        """Sets the username and password."""
        self.username = username
        self.password = password

    def set_token(self, token: str):
        """Sets the current token."""
        logger.info(f"Setting JWT")
        self.current_token = token

    def add_session(self, session: str):
        """Adds a session to the active sessions list."""
        logger.info(f"Adding session")
        self.active_sessions.append(session)

    def remove_session(self, session: str):
        """Removes a session from the active sessions list."""
        logger.info(f"Removing session")
        if session in self.active_sessions:
            self.active_sessions.remove(session)