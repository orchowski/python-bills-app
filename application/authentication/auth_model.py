from peewee import TextField

from application.authentication.auth_db import BaseModel


class User(BaseModel):
    public_id = TextField()
    email = TextField()
    password = TextField()
