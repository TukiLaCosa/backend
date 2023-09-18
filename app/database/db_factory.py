from pony.orm import Database
from app.config import config

db = Database()

db.bind(**config.settings.database_sqlite_connection)
