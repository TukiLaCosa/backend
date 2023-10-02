from fastapi import APIRouter, status
from typing import List
from . import services
from .schemas import *


router = APIRouter(
    prefix="/players",
    tags=["players"],
)


@router.get("/")
def get_all() -> List[PlayerResponse]:
    players = services.get_all()
    return [PlayerResponse.model_validate(p) for p in players]


@router.post('/', status_code=status.HTTP_201_CREATED)
def create(new_person: PlayerCreationIn) -> PlayerCreationOut:
    player = services.create(new_person)
    return PlayerCreationOut.model_validate(player)


@router.get('/{id}')
def find_by_id(id: int) -> PlayerResponse:
    player = services.find_player_by_id(id)
    return PlayerResponse.model_validate(player)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete(id: int) -> None:
    services.delete(id)


@router.patch('/{id}')
def update(id: str, update_data: PlayerUpdateIn) -> PlayerResponse:
    player = services.update(id, update_data)
    return PlayerResponse.model_validate(player)
