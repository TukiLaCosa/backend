from pony.orm import db_session
from app.database.models import Game, Card, Player
from ..players.schemas import PlayerRol
from ..cards.schemas import CardType, CardResponse
from ..websockets.utils import player_connections
from .utils import Events
from .schemas import RoundDirection
import random
import asyncio


async def send_player_between_us_event(to_player_id: int, player_id: int, player_name: str):
    json_msg = {
        "event": Events.BETWEEN_US_CARD_PLAYED,
        "player_id": player_id,
        "player_name": player_name
    }
    await player_connections.send_event_to(to_player_id, json_msg)


async def send_round_and_round_start_event(game_name: str):
    json_msg = {
        "event": Events.ROUND_AND_ROUND_START
    }
    await player_connections.send_event_to_all_players_in_game(game_name, json_msg)


@db_session
def process_between_us_card(game: Game, player: Player, card: Card, objective_player: Player):
    game.discard_deck.add(card)
    player.hand.remove(card)

    asyncio.ensure_future(send_player_between_us_event(
        objective_player.id, player.id, player.name))


@db_session
def process_round_and_round_card(game: Game, player: Player, card: Card):
    game.discard_deck.add(card)
    player.hand.remove(card)

    asyncio.ensure_future(send_round_and_round_start_event(game.name))


@db_session
def process_getout_of_here_card(game: Game, player: Player, card: Card, objective_player: Player):
    # Intercambio de posiciones entre los jugadores
    tempPosition = player.position
    player.position = objective_player.position
    objective_player.position = tempPosition

    game.discard_deck.add(card)
    player.hand.remove(card)
