from typing import List
from fastapi import WebSocket, HTTPException, status
from app.database.models import Game, Player
from pony.orm import *
from .schemas import *
from ..websockets.utils import player_connections, get_players_id


class Events(str, Enum):
    GAME_CREATED = 'game_created'
    GAME_UPDATED = 'game_updated'
    GAME_DELETED = 'game_deleted'
    GAME_STARTED = 'game_started'
    PLAYER_JOINED = 'player_joined'
    PLAYER_INIT_HAND = 'player_init_hand'


@db_session
def find_game_by_name(game_name: str):
    game = Game.get(name=game_name)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )

    return game


@db_session
def verify_game_can_start(name: str, host_player_id: int):
    game = find_game_by_name(name)
    players_joined = count(game.players)

    if game.status == GameStatus.STARTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The game has already started."
        )

    if not 4 <= players_joined <= 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The number of players joined ({players_joined}) is not allowed."
        )

    if game.host.id != host_player_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only the host player can start the game."
        )


@db_session
def list_of_unstarted_games() -> List[GameResponse]:
    games = Game.select(lambda game: game.status !=
                        GameStatus.STARTED and game.status != GameStatus.ENDED)
    games_list = [GameResponse(
        name=game.name,
        min_players=game.min_players,
        max_players=game.max_players,
        host_player_id=game.host.id,
        status=game.status,
        is_private=game.password is not None,
        num_of_players=len(game.players)
    ) for game in games]
    return games_list


@db_session
def list_of_games() -> List[GameResponse]:
    games = Game.select()
    games_list = [GameResponse(
        name=game.name,
        min_players=game.min_players,
        max_players=game.max_players,
        host_player_id=game.host.id,
        status=game.status,
        is_private=game.password is not None,
        num_of_players=len(game.players)
    ) for game in games]
    return games_list


@db_session
async def send_initial_cards(game_name: str):
    playersID = get_players_id(game_name)

    for idx in playersID:
        player = Player.get(id=idx)
        hand_cards = [card.id for card in player.hand]
        json_msg = {
            "event": Events.PLAYER_INIT_HAND,
            "game_name": game_name,
            "player_id": player.id,
            "hand_cards": hand_cards
        }
        await player_connections.send_event_to(player_id=player.id, message=json_msg)
