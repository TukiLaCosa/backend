from pony.orm import db_session, select
from app.database.models import Game, Card, Player
from ..players.schemas import PlayerRol
from ..cards.schemas import CardType, CardResponse
from ..websockets.utils import player_connections
from .utils import Events
from .schemas import RoundDirection, GameStatus
from ..players.utils import get_player_name_by_id
import random
import asyncio


async def send_players_eliminated_event(game: Game, killer_id: int, killer_name: str, eliminated_id: int, eliminated_name: str):
    players_positions = {}
    for p in game.players:
        if p.rol != PlayerRol.ELIMINATED:
            players_positions[p.id] = p.position

    json_msg = {
        "event": Events.PLAYER_ELIMINATED,
        "killer_player_id": killer_id,
        "killer_player_name": killer_name,
        "eliminated_player_id": eliminated_id,
        "eliminated_player_name": eliminated_name,
        "players_positions": players_positions
    }
    for p in game.players:
        await player_connections.send_event_to(p.id, json_msg)


async def send_players_whiskey_event(game: Game, player_id: int, player_name: str):
    json_msg = {
        "event": Events.WHISKEY_CARD_PLAYED,
        "player_id": player_id,
        "player_name": player_name
    }
    await player_connections.send_event_to_other_players_in_game(game.name, json_msg, player_id)


async def send_resolute_card_played_event(game: Game, player_id: int, option_cards: list[int]):
    json_msg = {
        "event": Events.RESOLUTE_CARD_PLAYED,
        "option_cards": option_cards
    }
    await player_connections.send_event_to(player_id, json_msg)

async def send_seduction_done_event(player_id: int, objective_player_id: int):
    json_msg = {
        "event": Events.SEDUCTION_DONE
    }
    await player_connections.send_event_to(player_id, json_msg)
    await player_connections.send_event_to(objective_player_id, json_msg)


@db_session
def process_flamethrower_card(game: Game, player: Player, objective_player: Player):
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

    asyncio.ensure_future(send_players_eliminated_event(game=game,
                                                        killer_id=player.id,
                                                        killer_name=player.name,
                                                        eliminated_id=objective_player.id,
                                                        eliminated_name=objective_player.name))


@db_session
def process_analysis_card(game: Game, player: Player, objective_player: Player):
    result = [CardResponse(id=c.id,
                           number=c.number,
                           type=c.type,
                           subtype=c.subtype,
                           name=c.name,
                           description=c.description
                           ) for c in objective_player.hand]

    return result


@db_session
def process_suspicious_card(game: Game, player: Player, objective_player: Player):
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

    return result


@db_session
def process_whiskey_card(game: Game, player: Player):
    asyncio.ensure_future(send_players_whiskey_event(
        game, player.id, player.name))


@db_session
def process_resolute_card(game: Game, player: Player, card: Card):
    game.discard_deck.add(card)
    player.hand.remove(card)

    random_draw_deck_cards = select(
        c for c in game.draw_deck if 2 <= c.id and c.id <= 88).random(3)
    random_discard_deck_cards = select(
        c for c in game.discard_deck if 2 <= c.id and c.id <= 88).random(3)

    while (len(random_draw_deck_cards) < 3):
        random_draw_deck_cards.append(random_discard_deck_cards.pop())

    option_cards_id = [card.id for card in random_draw_deck_cards]

    asyncio.ensure_future(send_resolute_card_played_event(
        game, player.id, option_cards_id))


@db_session
def process_watch_your_back_card(game: Game, player: Player):
    if game.round_direction == RoundDirection.CLOCKWISE:
        game.round_direction = RoundDirection.COUNTERCLOCKWISE
    else:
        game.round_direction = RoundDirection.CLOCKWISE


@db_session
def process_change_places_card(game: Game, player: Player, objective_player: Player):
    # Intercambio de posiciones entre los jugadores
    tempPosition = player.position
    player.position = objective_player.position
    objective_player.position = tempPosition

    # enviar evento de intercambio de lugar


@db_session
def process_better_run_card(game: Game, player: Player, objective_player: Player):
    # Intercambio de posiciones entre los jugadores
    tempPosition = player.position
    player.position = objective_player.position
    objective_player.position = tempPosition

    # enviar evento de cambio de lugar


@db_session
def process_card_exchange(player: Player, objective_player: Player, player_card: Card, objective_player_card: Card):
    player.hand.remove(player_card)
    player.hand.add(objective_player_card)

    objective_player.hand.remove(objective_player_card)
    objective_player.hand.add(player_card)

    # enviar evento de intercambio de carta


@db_session
def process_seduction_card(game: Game, player: Player, objective_player: Player,
                           card_to_exchange: Card):
    objective_player_hand_list = list(objective_player.hand)
    eligible_cards = [
        c for c in objective_player_hand_list if c.type != CardType.THE_THING]
    random_card = random.choice(eligible_cards)

    process_card_exchange(player, objective_player,
                          card_to_exchange, random_card)

    asyncio.ensure_future(send_seduction_done_event(
        player.id, objective_player.id))
