from pony.orm import *
from .defense_functions import *
from app.database import Intention


@db_session
def create_intention(action_type: ActionType, player: Player, objective_player: Player) -> Intention:
    return Intention(
        action_type=action_type,
        player=player,
        objective_player=objective_player
    )


@db_session
def conclude_intention():
    pass
