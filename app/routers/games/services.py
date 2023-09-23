from pony.orm import *
from app.database.models import Game, Player
from .schemas import *
from fastapi import HTTPException, status


@db_session
def create_game(game_data: GameCreationIn) -> GameCreationOut:

    host = Player.get(id=game_data.host_player_id)
    if host is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="player not found")

    if host.game_hosting is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The host is already hosting a game")

    if Game.exists(name=game_data.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The game name is already used")

    new_game = Game(
        name=game_data.name,
        min_players=game_data.min_players,
        max_players=game_data.max_players,
        password=game_data.password,
        host=host
    )

    host.game = new_game.name
    return GameCreationOut(
        name=new_game.name,
        status=new_game.status,
        min_players=new_game.min_players,
        max_players=new_game.max_players,
        is_private=new_game.password is not None,
        host_player_id=new_game.host.id
    )
