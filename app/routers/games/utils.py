from typing import List
from fastapi import WebSocket, HTTPException, status
from app.database.models import Game, Player, Card
from pony.orm import *
from .schemas import *
from ..websockets.utils import player_connections, get_players_id
from ..players.schemas import PlayerRol


class Events(str, Enum):
    GAME_CREATED = 'game_created'
    GAME_UPDATED = 'game_updated'
    GAME_DELETED = 'game_deleted'
    GAME_STARTED = 'game_started'
    GAME_CANCELED = 'game_canceled'
    PLAYER_JOINED = 'player_joined'
    PLAYER_LEFT = 'player_left'
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
def verify_game_can_be_canceled(game_name: str, host_player_id: int):
    game = find_game_by_name(game_name)

    if game.status != GameStatus.UNSTARTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The game is not in unstarted status"
        )
    if game.host.id != host_player_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only the host player can cancel the game."
        )


@db_session
def verify_game_can_be_abandon(game_name: str, player_id: int):
    game = find_game_by_name(game_name)
    player = Player.get(id=player_id)

    if game.status != GameStatus.UNSTARTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The game is not in unstarted status"
        )
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    if player not in game.players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player not in the game"
        )
    if player == game.host:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Host of the game can only cancel the game"
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


@db_session
def verify_discard_can_be_done(game_name: str, game_data: DiscardInformationIn):
    game = Game.get(name=game_name)
    player = Player.get(id=game_data.player_id)
    card = Card.get(id=game_data.card_id)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )

    is_player_in_game = select(
        p for p in game.players if (p.id == player.id)).exists()
    is_card_in_hand = select(
        c for c in player.hand if (c.id == card.id)).exists()

    if not is_player_in_game:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The player is not in the game"
        )
    if not is_card_in_hand:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The card doesn't belong to the player"
        )
    if card.type == CardType.THE_THING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The Thing cannot be discarded"
        )
    if game.turn != player.position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="It's not the turn of the player"
        )
    if player.role == PlayerRol.INFECTED and card.name == '¡Infectado!':
        infected_count = select(count(c)
                                for c in player.hand if c.name == '¡Infectado!')
        if infected_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The player is infected and cannot discard the card"
            )
