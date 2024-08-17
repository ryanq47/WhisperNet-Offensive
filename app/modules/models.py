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
    # id = db.Column(db.Integer, autoincrement=True)
    password = db.Column(db.String, nullable=False)
