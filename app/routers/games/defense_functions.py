from pony.orm import *
from app.database.models import Player
from ..cards.schemas import CardDefenseName
from enum import Enum


class ActionType(str, Enum):
    EXCHANGE_OFFER = "exchange_offer"
    CHANGE_PLACES = "change_places"
    BETTER_RUN = "better_run"
    FLAMETHROWER = "flamethrower"


response_to_action_type = {
    ActionType.EXCHANGE_OFFER: [
        CardDefenseName.SCARY,
        CardDefenseName.NO_THANKS,
        CardDefenseName.MISSED
    ],
    ActionType.CHANGE_PLACES: [CardDefenseName.I_AM_COMFORTABLE],
    ActionType.BETTER_RUN: [CardDefenseName.I_AM_COMFORTABLE],
    ActionType.FLAMETHROWER: [CardDefenseName.NO_BARBECUE]
}


@db_session
def player_cards_to_defend_himself(action_type: ActionType, player: Player) -> list[int]:
    defense_cards = response_to_action_type[action_type]
    player_defense_cards = []

    for card in player.hand.select():
        if card.name in defense_cards:
            player_defense_cards.append(card.id)

    return player_defense_cards
