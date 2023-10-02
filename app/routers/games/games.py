from fastapi import APIRouter, status, HTTPException
from typing import List
from . import services
from .schemas import *
from ..players.schemas import PlayerResponse


router = APIRouter(
    prefix="/games",
    tags=["games"],
)


@router.get("/", response_model=list[GameResponse], status_code=status.HTTP_200_OK)
def get_games():
    return services.get_games()


@router.get("/{game_name}", response_model=GameInformationOut, status_code=status.HTTP_200_OK)
def get_game_information(game_name: str):
    return services.get_game_information(game_name)


@router.post("/", response_model=GameCreationOut, status_code=status.HTTP_201_CREATED)
def create_game(game_data: GameCreationIn):
    return services.create_game(game_data)


@router.patch("/{game_name}", response_model=GameUpdateOut, status_code=status.HTTP_200_OK)
def update_game(game_name: str, game_data: GameUpdateIn):
    return services.update_game(game_name, game_data)


@router.delete("/{game_name}", status_code=status.HTTP_200_OK)
def delete_game(game_name: str):
    return services.delete_game(game_name)


@router.patch("/join/{game_name}", response_model=GameInformationOut, status_code=status.HTTP_200_OK)
def join_player(game_name: str, game_data: GameInformationIn):
    return services.join_player(game_name, game_data)
