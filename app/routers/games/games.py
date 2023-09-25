from fastapi import APIRouter, status, HTTPException
from typing import List
from . import services
from .schemas import *


router = APIRouter(
    prefix="/games",
    tags=["games"],
)


@router.get("/", response_model=list[GameResponse])
def get_games():
    return services.get_games()


@router.post("/", response_model=GameCreationOut, status_code=status.HTTP_201_CREATED)
def create_game(game_data: GameCreationIn):
    return services.create_game(game_data)
