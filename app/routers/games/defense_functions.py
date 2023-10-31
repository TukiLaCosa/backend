from pony.orm import *
from app.database.models import Player
from ..cards.schemas import CardActionName, CardDefenseName
from enum import Enum


class ActionType(str, Enum):
    EXCHANGE_OFFER = "Ofrecimiento de intercambio"
    CHANGE_PLACES = CardActionName.CHANGE_PLACES.value
    BETTER_RUN = CardActionName.BETTER_RUN.value
    FLAMETHROWER = CardActionName.FLAMETHROWER.value


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
def player_can_defend_himself(action_type: ActionType, player: Player) -> list[int]:
    defense_cards = response_to_action_type[action_type]
    player_defense_cards = []

    for card in player.hand:
        if card.name in defense_cards:
            player_defense_cards.append(card.id)

    return player_defense_cards
