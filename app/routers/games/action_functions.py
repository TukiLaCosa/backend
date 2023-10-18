from pony.orm import db_session
from app.database.models import Game, Card, Player
from ..players.schemas import PlayerRol
from ..cards.schemas import CardType, CardResponse
from ..websockets.utils import player_connections
from .utils import Events
from .schemas import RoundDirection
import random


@db_session
def process_flamethrower_card(game: Game, player: Player,
                              card: Card, objective_player: Player):
    objective_player.rol = PlayerRol.ELIMINATED

    # Las cartas del jugador eliminado van al mazo de descarte
    # salvo sea que sea la carta 'La Cosa'
    for c in objective_player.hand:
        if c.type != CardType.THE_THING:
            game.discard_deck.add(c)
            objective_player.hand.remove(c)

    # Reacomodo las posiciones
    for p in game.players:
        if p.position > objective_player.position:
            p.position -= 1
    objective_player.position = -1

    # Falta implementar Evento por WS
    
    game.discard_deck.add(card)
    player.hand.remove(card)


@db_session
def process_analysis_card(game: Game, player: Player,
                          card: Card, objective_player: Player):
    result = [CardResponse(id=c.id,
                           number=c.number,
                           type=c.type,
                           subtype=c.subtype,
                           name=c.name,
                           description=c.description
                           ) for c in objective_player.hand]
    game.discard_deck.add(card)
    player.hand.remove(card)
    return result


@db_session
def process_suspicious_card(game: Game, player: Player,
                            card: Card, objective_player: Player):
    objective_player_hand_list = list(objective_player.hand)
    random_card = random.choice(objective_player_hand_list)
    result = CardResponse(
        id=random_card.id,
        number=random_card.number,
        type=random_card.type,
        subtype=random_card.subtype,
        name=random_card.name,
        description=random_card.description
    )
    game.discard_deck.add(card)
    player.hand.remove(card)
    return result


@db_session
def process_whiskey_card(game: Game, player: Player, card: Card):
    # Falta implementar evento por WS
    game.discard_deck.add(card)
    player.hand.remove(card)


@db_session
def process_watch_your_back_card(game: Game, player: Player, card: Card):
    if game.round_direction == RoundDirection.CLOCKWISE:
        game.round_direction = RoundDirection.COUNTERCLOCKWISE
    else:
        game.round_direction = RoundDirection.CLOCKWISE

    game.discard_deck.add(card)
    player.hand.remove(card)


@db_session
def process_change_places_card(game: Game, player: Player, card: Card, objective_player: Player):
    # Intercambio de posiciones entre los jugadores
    tempPosition = player.position
    player.position = objective_player.position
    objective_player.position = tempPosition

    game.discard_deck.add(card)
    player.hand.remove(card)


@db_session
def process_better_run_card(game: Game, player: Player,
                            card: Card, objective_player: Player):
    # Intercambio de posiciones entre los jugadores
    tempPosition = player.position
    player.position = objective_player.position
    objective_player.position = tempPosition

    game.discard_deck.add(card)
    player.hand.remove(card)


@db_session
def process_seduction_card(game: Game, player: Player,
                           card: Card, objective_player: Player,
                           card_to_exchange: Card):
    objective_player_hand_list = list(objective_player.hand)
    eligible_cards = [
        c for c in objective_player_hand_list if c.type != CardType.THE_THING]
    random_card = random.choice(eligible_cards)

    player.hand.add(random_card)
    player.hand.remove(card_to_exchange)
    objective_player.hand.remove(random_card)
    objective_player.hand.add(card_to_exchange)

    game.discard_deck.add(card)
    player.hand.remove(card)
