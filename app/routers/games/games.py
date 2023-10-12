from fastapi import APIRouter, status, HTTPException, WebSocket
from typing import List
from . import services
from . import utils
from .schemas import *
from ..players.schemas import PlayerResponse
from ..websockets.utils import player_connections


router = APIRouter(
    prefix="/games",
    tags=["games"],
)


@router.get("/", response_model=list[GameResponse], status_code=status.HTTP_200_OK)
def get_unstarted_games():
    return services.get_unstarted_games()


@router.get("/{game_name}", response_model=GameInformationOut, status_code=status.HTTP_200_OK)
def get_game_information(game_name: str):
    return services.get_game_information(game_name)


@router.post("/", response_model=GameCreationOut, status_code=status.HTTP_201_CREATED)
async def create_game(game_data: GameCreationIn):
    new_game = services.create_game(game_data)

    json_msg = {
        "event": utils.Events.GAME_CREATED,
        "game_name": new_game.name
    }
    await player_connections.broadcast(json_msg)

    return new_game


@router.patch("/{name}/init")
async def start(name: str, host_player_id: int) -> GameStartOut:
    utils.verify_game_can_start(name, host_player_id)
    game = services.start_game(name)

    json_msg = {
        "event": utils.Events.GAME_STARTED,
        "game_name": game.name
    }
    await player_connections.broadcast(json_msg)

    return game


@router.patch("/{game_name}", response_model=GameUpdateOut, status_code=status.HTTP_200_OK)
async def update_game(game_name: str, game_data: GameUpdateIn):
    game_updated = services.update_game(game_name, game_data)

    json_msg = {
        "event": utils.Events.GAME_UPDATED,
        "game_name": game_updated.name
    }
    await player_connections.broadcast(json_msg)

    return game_updated


@router.delete("/{game_name}", status_code=status.HTTP_200_OK)
async def delete_game(game_name: str):
    services.delete_game(game_name)

    json_msg = {
        "event": utils.Events.GAME_DELETED,
        "game_name": game_name
    }
    await player_connections.broadcast(json_msg)

    return {"message": "Game deleted"}


@router.patch("/join/{game_name}", response_model=GameInformationOut, status_code=status.HTTP_200_OK)
async def join_player(game_name: str, game_data: GameInformationIn):
    game = services.join_player(game_name, game_data)

    json_msg = {
        "event": utils.Events.PLAYER_JOINED,
        "player_id": game_data.player_id,
        "game_name": game.name
    }
    await player_connections.broadcast(json_msg)

    return game
