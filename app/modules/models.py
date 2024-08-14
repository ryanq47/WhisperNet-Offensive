from flask_sqlalchemy import SQLAlchemy
from modules.instances import Instance
import datetime

db = Instance().db_engine

# change id to user_id

class User(db.Model):
    """
        ORM mapping for users

    """
    __tablename__ = "user"

    username = db.Column(
        db.String, unique=True, nullable=False
    )  # non nullable, but unique
    uuid = db.Column(
        db.String, primary_key=True
    )  # prim key, allows for changing actual username
    #id = db.Column(db.Integer, autoincrement=True)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return ""

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated


class Token(db.Model):
    """
        ORM mapping for tokens

    """
    __tablename__ = 'tokens'

    # needs some work
    '''ate
        id: id of row, used for indexing/primary key
        uuid: user id (UUID). NOT uniuqe, can have mult tokens per user. NOT nullable
        token: Active token, unique. do not want repeat tokens. NOT nullable
        created_at: timestamp
        expires_at: timestamp when it expires
        active: is active or not (up for debate)


    Note, need to figure out if we are storing UUID as string or binary too
    '''

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(36), index=True, nullable=False)  # Adjust length if using UUIDs
    token = db.Column(db.String(256), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)

    def is_active(self):
        """Check if the token is still active and not expired."""
        return self.active and (self.expires_at > datetime.datetime.utcnow())
