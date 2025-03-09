from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from modules.utils import get_utc_datetime

# from modules.log import log

# logger = log(__name__)


# Create the engine and base
# engine = create_engine("sqlite:///credstore.db", echo=True)
Base = declarative_base()


# Define the Credential model
class Credential(Base):
    __tablename__ = "credentials"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    realm = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    date_added = Column(DateTime, default=get_utc_datetime())


class CredStore:
    """
    A class to manage credentials using SQLAlchemy and SQLite.

    Attributes:
        engine: SQLAlchemy engine for connecting to the SQLite database.
        session: SQLAlchemy session for performing database operations.
    """

    def __init__(self):
        """
        Initializes the CredStore instance.

        - Creates a SQLite database connection.
        - Creates the table(s) if they don't already exist.
        - Initializes a SQLAlchemy session for database operations.
        """
        self.engine = create_engine("sqlite:///app/instance/credstore.db", echo=True)
        Base.metadata.create_all(self.engine)  # Ensure tables are created
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_credential(self, username, password, realm=None, notes=None):
        """
        Adds a new credential to the database.

        Args:
            username (str): The username for the credential.
            password (str): The password for the credential.
            realm (str, optional): The realm or domain associated with the credential. Default is None.
            notes (str, optional): Additional notes for the credential. Default is None.

        Returns:
            None
        """
        new_credential = Credential(
            username=username, password=password, realm=realm, notes=notes
        )
        self.session.add(new_credential)
        self.session.commit()

    def get_all_credentials(self):
        """
        Retrieves all credentials from the database.

        Returns:
            list: A list of Credential objects representing all credentials.
        """
        return self.session.query(Credential).all()

    def delete_credential(self, credential_id: str):
        """
        Deletes a credential from the database by its ID.

        Args:
            credential_id (int): The ID of the credential to delete.

        Returns:
            None
        """
        credential = self.session.query(Credential).filter_by(id=credential_id).first()
        if credential:
            self.session.delete(credential)
            self.session.commit()

    # Retrieve a single credential by ID
    def get_credential(self, credential_id: str):
        """
        Fetch a single credential by its ID.

        Args:
            credential_id (int): The ID of the credential to retrieve.

        Returns:
            Credential: The credential object if found, otherwise None.
        """

        # note: not including first, for 2 reasons:
        # 1: Incase of cred id clash, all the creds come back
        # 2: Keeps this object iterable, which allows it to work with the serialize_credentials function in credstore plugin, which keeps a consistent output from the api
        return self.session.query(Credential).filter_by(id=credential_id)  # .first()


# Example usage
if __name__ == "__main__":
    c = CredStore()
    c.add_credential("user1", "pass1", "example.com", "First credential")
    credentials = c.get_all_credentials()
    for cred in credentials:
        print(
            f"{cred.id}: {cred.username}, {cred.password}, {cred.realm}, {cred.notes}, {cred.date_added}"
        )
