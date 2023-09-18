from pony.orm import PrimaryKey, Required, Set
from app.database import db


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)


class Game(db.Entity):
    name = PrimaryKey(str)
