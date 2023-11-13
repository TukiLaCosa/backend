from pony.orm import *
from .defense_functions import *
from app.database import Intention, Game, Player
from ..cards.services import find_card_by_id
from app.routers.websockets.utils import player_connections
import asyncio
from .services import (
    find_game_by_name,
    process_change_places_card,
    process_better_run_card,
    process_flamethrower_card,
    process_card_exchange
)


async def send_intention_event(action_type: ActionType, player: Player, objective_player: Player):
    json_msg = {
        "event": action_type,
        "defense_cards": player_cards_to_defend_himself(action_type, objective_player),
        "player_id": player.id
    }

    await player_connections.send_event_to(objective_player.id, json_msg)


@db_session
def create_intention_in_game(game: Game, action_type: ActionType, player: Player, objective_player: Player, exchange_payload={}) -> Intention:
    intention = Intention(
        action_type=action_type,
        player=player,
        objective_player=objective_player,
        game=game,
        exchange_payload=exchange_payload
    )
    game.intention = intention

    asyncio.ensure_future(send_intention_event(action_type, player, objective_player))

    return intention


@db_session
def set_objective_card_in_exchange_payload(game: Game, objective_card_id: int):
    game.intention.exchange_payload['objective_card_id'] = objective_card_id


@db_session
def process_intention_in_game(game_name) -> Intention:
    game: Game = find_game_by_name(game_name)
    intention: Intention = game.intention
    player = intention.player
    objective_player = intention.objective_player

    match intention.action_type:
        case ActionType.CHANGE_PLACES:
            process_change_places_card(game, player, objective_player)

        case ActionType.BETTER_RUN:
            process_better_run_card(game, player, objective_player)

        case ActionType.FLAMETHROWER:
            process_flamethrower_card(game, player, objective_player)

    return intention


@db_session
def clean_intention_in_game(game_name):
    game: Game = find_game_by_name(game_name)
    Intention.get(game=game).delete()


@db_session
def get_intention_in_game(game_name: str) -> Intention:
    game: Game = find_game_by_name(game_name)

    return game.intention
