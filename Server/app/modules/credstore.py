from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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
    date_added = Column(DateTime, default=datetime.utcnow)


class CredStore:
    def __init__(self):
        self.engine = create_engine("sqlite:///app/instance/credstore.db", echo=True)
        # Create the table(s) if they don't exist
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    # Add a new credential
    def add_credential(self, username, password, realm=None, notes=None):
        new_credential = Credential(
            username=username, password=password, realm=realm, notes=notes
        )
        self.session.add(new_credential)
        self.session.commit()

    # Query all credentials
    def get_all_credentials(self):
        return self.session.query(Credential).all()

    # Delete a credential
    def delete_credential(self, credential_id):
        credential = self.session.query(Credential).filter_by(id=credential_id).first()
        if credential:
            self.session.delete(credential)
            self.session.commit()


# Example usage
if __name__ == "__main__":
    c = CredStore()
    c.add_credential("user1", "pass1", "example.com", "First credential")
    credentials = c.get_all_credentials()
    for cred in credentials:
        print(
            f"{cred.id}: {cred.username}, {cred.password}, {cred.realm}, {cred.notes}, {cred.date_added}"
        )
