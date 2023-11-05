from pony.orm import *
from .defense_functions import *
from app.database import Intention, Game, Player
from ..cards.services import find_card_by_id
from .services import (
    find_game_by_name,
    process_change_places_card,
    process_better_run_card,
    process_flamethrower_card,
    process_card_exchange
)


@db_session
def create_intention_in_game(game: Game, action_type: ActionType, player: Player, objective_player: Player, exchange_payload=None) -> Intention:
    intention = Intention(
        action_type=action_type,
        player=player,
        objective_player=objective_player,
        game=game,
        exchange_payload=exchange_payload
    )
    game.intention = intention

    return intention


@db_session
def process_intention_in_game(game_name) -> Intention:
    game: Game = find_game_by_name(game_name)
    intention: Intention = game.intention
    player = intention.player
    objective_player = intention.objective_player

    match intention.action_type:
        case ActionType.EXCHANGE_OFFER:
            exchange_info = intention.exchange_payload

            player_card = find_card_by_id(exchange_info.card_id)
            objective_player_card = find_card_by_id(
                exchange_info.objective_card_id)

            process_card_exchange(player, objective_player,
                                  player_card, objective_player_card)

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
