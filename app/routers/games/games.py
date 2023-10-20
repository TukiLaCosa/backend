from fastapi import APIRouter, status
from pony.orm import db_session, select
from app.database.models import Player
from . import services
from . import utils
from .schemas import *
from ..websockets.utils import player_connections
from .utils import find_game_by_name
from ..players.utils import get_player_name_by_id
from ..cards.utils import get_card_name_by_id


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

    await utils.send_initial_cards(name)

    json_msg = {
        "event": utils.Events.GAME_STARTED,
        "game_name": name
    }
    await player_connections.broadcast(json_msg)

    return game


@router.patch("/{game_name}", response_model=GameUpdateOut, status_code=status.HTTP_200_OK)
async def update_game(game_name: str, game_data: GameUpdateIn):
    game_updated = services.update_game(game_name, game_data)

    json_msg = {
        "event": utils.Events.GAME_UPDATED,
        "game_name": game_name
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


@router.delete("/cancel/{game_name}", status_code=status.HTTP_200_OK)
async def cancel_game(game_name: str, player_id: int):
    utils.verify_game_can_be_canceled(game_name, player_id)

    json_msg = {
        "event": utils.Events.GAME_CANCELED,
        "game_name": game_name
    }
    await player_connections.send_event_to_other_players_in_game(game_name=game_name,
                                                                 message=json_msg,
                                                                 excluded_id=player_id)

    services.cancel_game(game_name)

    json_msg["event"] = utils.Events.GAME_DELETED
    await player_connections.broadcast(message=json_msg)

    return {"message": "Game canceled"}


@router.patch("/leave/{game_name}", response_model=GameInformationOut, status_code=status.HTTP_200_OK)
async def leave_game(game_name: str, player_id: int):
    utils.verify_game_can_be_abandon(game_name, player_id)
    json_msg = {
        "event": utils.Events.PLAYER_LEFT,
        "game_name": game_name
    }
    await player_connections.send_event_to_other_players_in_game(game_name=game_name,
                                                                 message=json_msg,
                                                                 excluded_id=player_id)

    gameInformation = services.leave_game(game_name, player_id)

    json_msg["event"] = utils.Events.GAME_UPDATED

    await player_connections.broadcast(message=json_msg)

    return gameInformation


@router.patch("/{game_name}/discard", status_code=status.HTTP_200_OK)
async def discard_card(game_name: str, game_data: DiscardInformationIn):
    utils.verify_discard_can_be_done(game_name, game_data)
    game = services.discard_card(game_name, game_data)
    with db_session:
        player_id_turn = select(
            p for p in game.players if p.position == game.turn).first().id
    json_msg = {
        "event": utils.Events.NEW_TURN,
        "next_player_name": get_player_name_by_id(player_id_turn),
        "next_player_id": player_id_turn,
        "round_direction": game.round_direction
    }
    await player_connections.send_event_to_all_players_in_game(game_name, json_msg)
    return {"message": "Card discarded"}


@router.post("/{game_name}/play-action-card", status_code=status.HTTP_200_OK)
async def play_action_card(game_name: str, play_info: PlayInformation):
    result = services.play_action_card(game_name, play_info)
    json_msg = {
        "event": utils.Events.PLAYED_CARD,
        "player_name": get_player_name_by_id(play_info.player_id),
        "card_name": get_card_name_by_id(play_info.card_id)
    }
    await player_connections.send_event_to_other_players_in_game(game_name, json_msg, play_info.player_id)

    with db_session:
        game = find_game_by_name(game_name)
        player_id_turn = select(
            p for p in game.players if p.position == game.turn).first().id
    json_msg = {
        "event": utils.Events.NEW_TURN,
        "next_player_name": get_player_name_by_id(player_id_turn),
        "next_player_id": player_id_turn,
        "round_direction": game.round_direction
    }
    await player_connections.send_event_to_all_players_in_game(game_name, json_msg)

    return result


@router.patch("/{game_name}/draw-card", status_code=status.HTTP_200_OK, response_model=CardResponse)
async def draw_card(game_name: str, game_data: DrawInformationIn):
    utils.verify_draw_can_be_done(game_name, game_data)
    draw_card_information = services.draw_card(game_name, game_data)

    json_msg = {
        "event": utils.Events.PLAYER_DRAW_CARD,
        "game_name": game_name,
        "player_name": get_player_name_by_id(game_data.player_id),
        "player_id": game_data.player_id,
        "next_card": draw_card_information.top_card_face
    }

    await player_connections.send_event_to_all_players_in_game(game_name=game_name,
                                                               message=json_msg)

    return draw_card_information.card
