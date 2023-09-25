from pony.orm import *
from app.database.models import Game, Player
from .schemas import *
from fastapi import HTTPException, status


@db_session
def get_games() -> list[GameResponse]:
    games = Game.select()
    games_list = [GameResponse(
        name=game.name,
        min_players=game.min_players,
        max_players=game.max_players,
        host_player_id=game.host.id,
        status=game.status,
        is_private=game.password is not None,
        players_joined=len(game.players)
    ) for game in games]
    return games_list


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


@db_session
def update_game(game_name: str, request_data: GameUpdateIn):
    game = Game.get(name=game_name)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    if game_name != request_data.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid game name")
    game.min_players = request_data.min_players
    game.max_players = request_data.max_players
    game.password = request_data.password
    return {"message": "Game updated"}


@db_session
def delete_game(game_name: str):
    game = Game.get(name=game_name)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    if game_name != game.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid game name")
    game.delete()
    return {"message": "Game deleted"}
