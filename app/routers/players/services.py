from pony.orm import *
from app.database.models import Player
from .schemas import *


@db_session
def get_all() -> list[PlayerOut]:
    players = Player.select()
    return [PlayerOut.model_validate(p) for p in players]


@db_session
def create(new_person: PlayerIn):
    player = Player(name=new_person.name, rol='ELIMINATED')
    return {"message": "Player added successfully"}
