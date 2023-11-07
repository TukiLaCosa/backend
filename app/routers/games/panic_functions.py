from pony.orm import db_session, select
from app.database.models import Game, Card, Player
from ..players.schemas import PlayerRol
from ..cards.schemas import CardType, CardResponse
from ..websockets.utils import player_connections
from .utils import Events, get_id_of_next_player_in_turn
from .schemas import RoundDirection
import random
import asyncio


async def send_ooops_card_played_event(game_name: str, player_name: str, player_id: int):
    json_msg = {
        "event": Events.OOOPS_CARD_PLAYED,
        "player_name": player_name,
        "player_id": player_id
    }
    await player_connections.send_event_to_other_players_in_game(game_name, json_msg, player_id)


async def send_player_between_us_event(to_player_id: int, player_id: int, player_name: str):
    json_msg = {
        "event": Events.BETWEEN_US_CARD_PLAYED,
        "player_id": player_id,
        "player_name": player_name
    }
    await player_connections.send_event_to(to_player_id, json_msg)


async def send_forgetful_card_played(player_id: int, player_name: str):
    json_msg = {
        "event": Events.FORGETFUL_CARD_PLAYED,
        "player_id": player_id,
        "player_name": player_name
    }
    await player_connections.send_event_to(player_id, json_msg)


async def send_round_and_round_start_event(game_name: str):
    json_msg = {
        "event": Events.ROUND_AND_ROUND_START
    }
    await player_connections.send_event_to_all_players_in_game(game_name, json_msg)


async def send_revelations_card_played_event(game_name: str, original_player_id: int, next_player_id: int):
    json_msg = {
        "event": Events.REVELATIONS_CARD_PLAYED,
        "original_player_id": original_player_id
    }
    await player_connections.send_event_to(next_player_id, json_msg)


async def send_one_two_card_played_event(player_id: int, player_name: str, player_list: list[int]):
    json_msg = {
        "event": Events.ONE_TWO_CARD_PLAYED,
        "player_id": player_id,
        "player_name": player_name,
        "possible_interchange_id": player_list
    }
    await player_connections.send_event_to(player_id, json_msg)


async def send_blind_date_selection_event(player_id: int):
    json_msg = {
        "event": Events.BLIND_DATE_SELECTION,
    }
    await player_connections.send_event_to(player_id, json_msg)


@db_session
def process_revelations_card(game: Game, player: Player):
    next_player_id = get_id_of_next_player_in_turn(game.name)
    asyncio.ensure_future(send_revelations_card_played_event(
        game.name, player.id, next_player_id))


@db_session
def process_one_two_card(game: Game, player: Player):
    players_in_game = len(
        select(p for p in game.players if p.rol != PlayerRol.ELIMINATED)[:])
    players_list: list[int] = []

    if players_in_game > 4:
        left_player_position = (player.position + 3) % players_in_game
        left_player: Player = select(
            p for p in game.players if p.position == left_player_position)
        right_player_position = (player.position - 3) % players_in_game
        right_player: Player = select(
            p for p in game.players if p.position == right_player_position)
        players_list.append(left_player.id)
        players_list.append(right_player.id)
    else:
        players_list.append(player.id)

    asyncio.ensure_future(send_one_two_card_played_event(
        player.id, player.name, players_list))


@db_session
def process_ooops_card(game: Game, player: Player):
    asyncio.ensure_future(send_ooops_card_played_event(
        game.name, player.name, player.id))


@db_session
def process_between_us_card(game: Game, player: Player, objective_player: Player):
    asyncio.ensure_future(send_player_between_us_event(
        objective_player.id, player.id, player.name))


@db_session
def process_forgetful_card(game: Game, player: Player):
    asyncio.ensure_future(send_forgetful_card_played(player.id, player.name))


@db_session
def process_round_and_round_card(game: Game, player: Player):
    asyncio.ensure_future(send_round_and_round_start_event(game.name))


@db_session
def process_getout_of_here_card(game: Game, player: Player, objective_player: Player):
    tempPosition = player.position
    player.position = objective_player.position
    objective_player.position = tempPosition


@db_session
def process_blind_date_card(game: Game, player: Player):
    asyncio.ensure_future(send_blind_date_selection_event(player.id))
