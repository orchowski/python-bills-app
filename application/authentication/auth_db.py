from peewee import Database, Proxy, Model

db_proxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = db_proxy


def initialize_database(database: Database):
    global db_proxy
    db_proxy.initialize(database)
