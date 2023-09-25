from pony.orm import *
from fastapi import HTTPException, status
from app.database.models import Player
from .schemas import *


@db_session
def get_all() -> list[Player]:
    return Player.select()[:]


@db_session
def create(new_person: PlayerCreationIn) -> Player:
    return Player(name=new_person.name)


@db_session
def find_by_id(id: int) -> Player:
    player = Player.get(id=id)

    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with id '{id}' not found."
        )

    return player


@db_session
def delete(id: int) -> None:
    find_by_id(id)
    Player[id].delete()


@db_session
def update(id: int, update_data: PlayerUpdateIn) -> Player:
    player = find_by_id(id)
    player.set(name=update_data.name)
    return player
