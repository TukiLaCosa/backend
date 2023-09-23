from pony.orm import *
from app.database.models import Player
from .schemas import *


@db_session
def get_all() -> list[PlayerResponse]:
    players = Player.select()
    return [PlayerResponse.model_validate(p) for p in players]


@db_session
def create(new_person: PlayerCreationIn) -> PlayerCreationOut:
    return Player(name=new_person.name)
