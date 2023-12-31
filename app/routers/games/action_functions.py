from pony.orm import db_session, select
from app.database.models import Game, Card, Player
from ..players.schemas import PlayerRol
from ..cards.schemas import CardType, CardResponse, CardSubtype
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


async def send_players_chagnge_event(game: Game, player_id: int, objective_player_id: int):
    json_msg = {
        "event": Events.CHANGE_DONE,
        "player_id": player_id,
        "objective_player_id": objective_player_id
    }
    await player_connections.send_event_to_all_players_in_game(game.name, json_msg)


async def send_players_exchagnge_event(game: Game, player_id: int, objective_player_id: int):
    json_msg = {
        "event": Events.EXCHANGE_DONE,
        "player_name": get_player_name_by_id(player_id),
        "objective_player_name": get_player_name_by_id(objective_player_id)
    }
    await player_connections.send_event_to_all_players_in_game(game.name, json_msg)


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


async def send_suspicious_card_played_event(player_id: int, card_name: str):
    json_msg = {
        "event": Events.SUSPICIOUS_CARD_PLAYED,
        "card_name": card_name
    }
    await player_connections.send_event_to(player_id, json_msg)
    await asyncio.sleep(5)


async def send_analysis_card_played_event(player_id: int, player_name: str, cards: list[str]):
    json_msg = {
        "event": Events.ANALYSIS_CARD_PLAYED,
        "cards": cards,
        "player_name": player_name
    }
    await player_connections.send_event_to(player_id, json_msg)
    await asyncio.sleep(5)


async def send_infected_event(infected_id: int, infected_name: str, the_thing_id: int, the_thing_name: str):
    json_msg = {
        "event": Events.NEW_INFECTED,
        "infected_id": infected_id,
        "infected_name": infected_name,
        "the_thing_id": the_thing_id,
        "the_thing_name": the_thing_name
    }
    await player_connections.send_event_to(infected_id, json_msg)
    await player_connections.send_event_to(the_thing_id, json_msg)


@db_session
def process_flamethrower_card(game: Game, player: Player, objective_player: Player):
    objective_player.rol = PlayerRol.ELIMINATED

    # Las cartas del jugador eliminado van al mazo de descarte
    # salvo sea que sea la carta 'La Cosa'
    for c in objective_player.hand:
        if c.type != CardType.THE_THING:
            game.discard_deck.add(c)
            objective_player.hand.remove(c)

    # Reacomodo el turno
    if game.turn != 0 and objective_player.position < player.position:
        game.turn = game.turn - 1

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
    result = {}
    result['cards'] = [c.name for c in objective_player.hand]
    result['objective_player_name'] = objective_player.name

    for i in range(1, (len(result['cards']))):
        result["cards"][i] = " " + result["cards"][i]

    asyncio.ensure_future(send_analysis_card_played_event(player.id,
                                                          objective_player.name, result['cards']))

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

    asyncio.ensure_future(send_suspicious_card_played_event(
        player.id, random_card.name))

    return result


@db_session
def process_whiskey_card(game: Game, player: Player):
    asyncio.ensure_future(send_players_whiskey_event(
        game, player.id, player.name))


@db_session
def process_resolute_card(game: Game, player: Player):
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
def process_watch_your_back_card(game: Game):
    if game.round_direction == RoundDirection.CLOCKWISE:
        game.round_direction = RoundDirection.COUNTERCLOCKWISE
    else:
        game.round_direction = RoundDirection.CLOCKWISE


@db_session
def process_change_places_card(game: Game, player: Player, objective_player: Player):
    tempPosition = player.position
    player.position = objective_player.position
    objective_player.position = tempPosition
    game.turn = player.position

    asyncio.ensure_future(send_players_chagnge_event(
        game, player.id, objective_player.id))


@db_session
def process_better_run_card(game: Game, player: Player, objective_player: Player):
    tempPosition = player.position
    player.position = objective_player.position
    objective_player.position = tempPosition
    game.turn = player.position

    asyncio.ensure_future(send_players_chagnge_event(
        game, player.id, objective_player.id))


@db_session
def process_card_exchange(game: Game, player: Player, objective_player: Player, player_card: Card, objective_player_card: Card):
    if (player.rol == PlayerRol.THE_THING and player_card.subtype == CardSubtype.CONTAGION):
        if objective_player.rol != PlayerRol.INFECTED:
            objective_player.rol = PlayerRol.INFECTED
            objective_player.game_last_infected = objective_player.game
            asyncio.ensure_future(send_infected_event(
                objective_player.id, objective_player.name, player.id, player.name))

    elif (objective_player.rol == PlayerRol.THE_THING and objective_player_card.subtype == CardSubtype.CONTAGION):
        if player.rol != PlayerRol.INFECTED:
            player.rol = PlayerRol.INFECTED
            player.game_last_infected = player.game
            asyncio.ensure_future(send_infected_event(
                player.id, player.name, objective_player.id, objective_player.name))

    player.hand.remove(player_card)
    player.hand.add(objective_player_card)

    objective_player.hand.remove(objective_player_card)
    objective_player.hand.add(player_card)


@db_session
def process_seduction_card(game: Game, player: Player, objective_player: Player,
                           card_to_exchange: Card):
    objective_player_hand_list = list(objective_player.hand)
    eligible_cards = [
        c for c in objective_player_hand_list if c.type != CardType.THE_THING]
    random_card = random.choice(eligible_cards)

    process_card_exchange(game, player, objective_player,
                          card_to_exchange, random_card)

    asyncio.ensure_future(send_players_exchagnge_event(
        game, player.id, objective_player.id))

    # asyncio.ensure_future(send_seduction_done_event(
    #    player.id, objective_player.id))
