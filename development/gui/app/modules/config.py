from yarl import URL
from app.modules.log import log

logger = log(__name__)

# Config singleton
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
        try:
            logger.info(f"Setting URL: {url}")
            self.url = URL(url)
        except Exception as e:
            logger.error(f"Error setting URL: {e}")

    def get_url(self) -> URL:
        """Gets the current URL."""
        try:
            return self.url
        except Exception as e:
            logger.error(f"Error getting URL: {e}")
            return None

    def set_credentials(self, username: str, password: str):
        """Sets the username and password."""
        try:
            self.username = username
            self.password = password
        except Exception as e:
            logger.error(f"Error setting credentials: {e}")

    def get_credentials(self) -> tuple:
        """Gets the username and password."""
        try:
            return self.username, self.password
        except Exception as e:
            logger.error(f"Error getting credentials: {e}")
            return None, None

    def set_token(self, token: str):
        """Sets the current token."""
        try:
            logger.info(f"Setting JWT")
            self.current_token = token
        except Exception as e:
            logger.error(f"Error setting token: {e}")

    def get_token(self) -> str:
        """Gets the current token."""
        try:
            return self.current_token
        except Exception as e:
            logger.error(f"Error getting token: {e}")
            return None

    def add_session(self, session: str):
        """Adds a session to the active sessions list."""
        try:
            logger.info(f"Adding session")
            self.active_sessions.append(session)
        except Exception as e:
            logger.error(f"Error adding session: {e}")

    def remove_session(self, session: str):
        """Removes a session from the active sessions list."""
        try:
            logger.info(f"Removing session")
            if session in self.active_sessions:
                self.active_sessions.remove(session)
        except Exception as e:
            logger.error(f"Error removing session: {e}")

    def get_active_sessions(self) -> list:
        """Gets the list of active sessions."""
        try:
            return self.active_sessions
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return []
