from pony.orm import *
from .defense_functions import *
from app.database import Intention, Game


@db_session
def create_intention_in_game(game: Game, action_type: ActionType, player: Player, objective_player: Player) -> Intention:
    intention = Intention(
        action_type=action_type,
        player=player,
        objective_player=objective_player,
        game=game
    )
    game.intention = intention

    return intention


@db_session
def conclude_intention():
    pass
