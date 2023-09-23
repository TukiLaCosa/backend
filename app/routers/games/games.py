from fastapi import APIRouter, status, HTTPException
from typing import List
from . import services
from .schemas import *


router = APIRouter(
    prefix="/games",
    tags=["games"],
)


# @router.get("/", response_model=List[GameCreationOut])
# def get_all_games() -> List[GameCreationOut]:
#     return services.get_all_games()


@router.post("/", response_model=GameCreationOut, status_code=status.HTTP_201_CREATED)
def create_game(game_data: GameCreationIn):
    return services.create_game(game_data)
    
    # try:
    #     return services.create_game(game_data)

    # except Exception as e:  # atrapa todas las exepciones
    #     # hace falta esto?
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
