from pony.orm import *
from typing import List
from app.database.models import Game, Player, Card
from .schemas import *
from ..players.schemas import PlayerRol
from fastapi import HTTPException, status
from .utils import *
from ..cards import services as cards_services
from ..cards.utils import find_card_by_id, verify_action_card, verify_panic_card
from ..players.utils import find_player_by_id, verify_card_in_hand, verify_player_not_in_quarentine
from ..cards.schemas import CardActionName, CardResponse, CardPanicName
from ..players.schemas import PlayerRol
from .action_functions import *
from .panic_functions import *
import random
from app.routers.games import utils


def get_unstarted_games() -> List[GameResponse]:
    games_list = list_of_unstarted_games()
    return games_list


@db_session
def get_game_information(game_name: str) -> GameInformationOut:
    game = Game.get(name=game_name)

    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Game not found')
    players_joined = game.players.select()[:]
    return GameInformationOut(name=game.name,
                              min_players=game.min_players,
                              max_players=game.max_players,
                              is_private=game.password is not None,
                              status=game.status,
                              host_player_name=game.host.name,
                              host_player_id=game.host.id,
                              num_of_players=len(game.players),
                              list_of_players=[PlayerResponse.model_validate(
                                  p) for p in players_joined]
                              )


@db_session
def create_game(game_data: GameCreationIn) -> GameCreationOut:
    host = Player.get(id=game_data.host_player_id)

    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    if host.game_hosting:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The host is already hosting a game")
    if Game.exists(name=game_data.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The game name is already used")

    new_game = Game(
        name=game_data.name,
        min_players=game_data.min_players,
        max_players=game_data.max_players,
        password=game_data.password,
        host=host
    )

    host.game = new_game.name

    return GameCreationOut(
        name=new_game.name,
        status=new_game.status,
        min_players=new_game.min_players,
        max_players=new_game.max_players,
        is_private=new_game.password is not None,
        host_player_id=new_game.host.id
    )


@db_session
def update_game(game_name: str, request_data: GameUpdateIn) -> GameUpdateOut:
    game = Game.get(name=game_name)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    if game_name != game.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid game name")

    game.min_players = request_data.min_players
    game.max_players = request_data.max_players
    game.password = request_data.password

    return GameUpdateOut(name=game.name,
                         min_players=game.min_players,
                         max_players=game.max_players,
                         is_private=game.password is not None,
                         status=game.status)


@db_session
def delete_game(game_name: str):
    game: Game = find_game_by_name(game_name)

    if game.status != GameStatus.ENDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The game is not ended."
        )

    for player in game.players:
        player.hand.clear()

    game.delete()


@db_session
def join_player(game_name: str, game_data: GameInformationIn) -> GameInformationOut:
    game = Game.get(name=game_name)
    player = Player.get(id=game_data.player_id)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    if player in game.players:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Player already in the game")
    if game.max_players <= len(game.players):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="The game is full")
    if game.password and game.password != game_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")
    if player.game is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="The player is already in another game")

    game.players.add(player)
    players_joined = game.players.select()[:]
    num_players_joined = len(players_joined)

    return GameInformationOut(name=game.name,
                              min_players=game.min_players,
                              max_players=game.max_players,
                              is_private=game.password is not None,
                              status=game.status,
                              host_player_name=game.host.name,
                              host_player_id=game.host.id,
                              num_of_players=num_players_joined,
                              list_of_players=[PlayerResponse.model_validate(
                                  p) for p in players_joined]
                              )


@db_session
def start_game(name: str) -> Game:
    game: Game = find_game_by_name(name)
    players_joined = count(game.players)

    deal_deck = cards_services.build_deal_deck(players_joined)
    cards_services.deal_cards_to_players(game, deal_deck)

    draw_deck = cards_services.build_draw_deck(
        deal_deck=deal_deck, players=players_joined)

    # Pongo los id de las cartas en draw_deck_order y luego hago el shuffle (mezclar)
    for card in draw_deck:
        game.draw_deck_order.append(card.id)
    random.shuffle(game.draw_deck_order)

    game.draw_deck.add(draw_deck)

    # setting the position and rol of the players
    for idx, player in enumerate(game.players):
        player.position = idx
        if cards_services.card_is_in_player_hand('La Cosa', player):
            player.rol = PlayerRol.THE_THING
        else:
            player.rol = PlayerRol.HUMAN

    game.status = GameStatus.STARTED
    game.turn = 0

    top_card_face = select(
        card for card in game.draw_deck if card.id == game.draw_deck_order[0]).first().type

    return GameStartOut(
        list_of_players=game.players,
        status=game.status,
        top_card_face=top_card_face
    )


@db_session
def cancel_game(game_name: str):
    game = Game.get(name=game_name)
    game.delete()


@db_session
def leave_game(game_name: str, player_id: int) -> GameInformationOut:
    game = Game.get(name=game_name)
    player = Player.get(id=player_id)
    game.players.remove(player)
    players_joined = game.players.select()[:]
    num_players_joined = len(players_joined)
    return GameInformationOut(name=game.name,
                              min_players=game.min_players,
                              max_players=game.max_players,
                              is_private=game.password is not None,
                              status=game.status,
                              host_player_name=game.host.name,
                              host_player_id=game.host.id,
                              num_of_players=num_players_joined,
                              list_of_players=[PlayerResponse.model_validate(
                                  p) for p in players_joined]
                              )


@db_session
def discard_card(game_name: str, game_data: DiscardInformationIn) -> Game:
    game: Game = Game.get(name=game_name)
    player: Player = Player.get(id=game_data.player_id)
    card = Card.get(id=game_data.card_id)
    if card in player.hand:
        player.hand.remove(card)
    if game and card:
        game.discard_deck.add(card)

    return game


async def finish_game(name: str) -> Game:
    with db_session:
        game: Game = find_game_by_name(name)
        try:
            verify_game_can_be_finished(game)
            game.status = GameStatus.ENDED

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    json_msg = {
        "event": utils.Events.GAME_ENDED,
    }

    await player_connections.send_event_to_all_players_in_game(game.name, json_msg)
    return game


@db_session
def play_action_card(game_name: str, play_info: PlayInformation):
    result = {"message": "Action card played"}
    game: Game = find_game_by_name(game_name)
    verify_player_in_game(play_info.player_id, game_name)
    player: Player = find_player_by_id(play_info.player_id)
    card: Card = find_card_by_id(play_info.card_id)
    verify_action_card(card)
    verify_card_in_hand(player, card)

    players_not_eliminated = select(
        p for p in game.players if p.rol != PlayerRol.ELIMINATED).count()

    # Lanzallamas
    if card.name == CardActionName.FLAMETHROWER:
        verify_player_in_game(play_info.objective_player_id, game_name)
        verify_adjacent_players(play_info.player_id,
                                play_info.objective_player_id,
                                players_not_eliminated - 1)
        objective_player: Player = find_player_by_id(
            play_info.objective_player_id)

        if game.turn != 0 and objective_player.position < player.position:
            game.turn = game.turn - 1

        process_flamethrower_card(game, player, card, objective_player)

    # Analisis
    if card.name == CardActionName.ANALYSIS:
        verify_player_in_game(play_info.objective_player_id, game_name)
        verify_adjacent_players(play_info.player_id,
                                play_info.objective_player_id,
                                players_not_eliminated - 1)
        objective_player: Player = find_player_by_id(
            play_info.objective_player_id)
        # Armo listado de cartas del jugador objetivo para enviar en el body response
        result = process_analysis_card(game, player, card, objective_player)

    # Hacha
    if card.name == CardActionName.AXE:
        pass

    # Sospecha
    if card.name == CardActionName.SUSPICIOUS:
        verify_player_in_game(play_info.objective_player_id, game_name)
        verify_adjacent_players(play_info.player_id,
                                play_info.objective_player_id,
                                players_not_eliminated - 1)
        objective_player: Player = find_player_by_id(
            play_info.objective_player_id)
        result = process_suspicious_card(game, player, card, objective_player)

    # Whisky
    if card.name == CardActionName.WHISKEY:
        process_whiskey_card(game, player, card)

    # Determinacion
    if card.name == CardActionName.RESOLUTE:
        pass

    # Vigila tus espaldas
    if card.name == CardActionName.WATCH_YOUR_BACK:
        process_watch_your_back_card(game, player, card)

    # Cambio de lugar
    if card.name == CardActionName.CHANGE_PLACES:
        verify_player_in_game(play_info.objective_player_id, game_name)
        verify_adjacent_players(play_info.player_id,
                                play_info.objective_player_id,
                                players_not_eliminated - 1)
        objective_player: Player = find_player_by_id(
            play_info.objective_player_id)
        process_change_places_card(game, player, card, objective_player)

    # Mas vale que corras
    if card.name == CardActionName.BETTER_RUN:
        verify_player_in_game(play_info.objective_player_id, game_name)
        objective_player: Player = find_player_by_id(
            play_info.objective_player_id)
        process_better_run_card(game, player, card, objective_player)

    # Seduccion (Ojo porque esta carta modifica la mano del jugador objetivo)
    if card.name == CardActionName.SEDUCTION:
        verify_player_in_game(play_info.objective_player_id, game_name)
        objective_player: Player = find_player_by_id(
            play_info.objective_player_id)
        card_to_exchange: Card = find_card_by_id(play_info.card_to_exchange)
        if card_to_exchange.type == CardType.THE_THING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The card to exchange cannot be The Thing"
            )
        verify_card_in_hand(player, card_to_exchange)
        process_seduction_card(
            game, player, card, objective_player, card_to_exchange)

    return result


@db_session
def draw_card(game_name: str, game_data: DrawInformationIn) -> DrawInformationOut:
    game: Game = find_game_by_name(game_name)
    player: Player = find_player_by_id(game_data.player_id)

    if len(game.draw_deck_order) == 1:
        merge_decks_of_card(game_name)

    top_card_id = game.draw_deck_order.pop(0)
    card = select(card for card in game.draw_deck if card.id ==
                  top_card_id).first()

    player.hand.add(card)
    game.draw_deck.remove(card)

    top_card_face = select(
        card for card in game.draw_deck if card.id == game.draw_deck_order[0]).first().type

    return DrawInformationOut(player_id=player.id,
                              card=CardResponse(number=card.number,
                                                type=card.type,
                                                subtype=card.subtype,
                                                name=card.name,
                                                description=card.description,
                                                id=card.id),
                              top_card_face=top_card_face)


@db_session
def get_game_result(name: str) -> GameResult:
    game: Game = find_game_by_name(name)

    if game.status != GameStatus.ENDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The game is not ended."
        )

    reason = ""
    winners = []
    losers = []

    if the_thing_is_eliminated(game):
        reason = "La Cosa fue eliminada de la partida."
        winners = game.players.select(lambda p: p.rol == PlayerRol.HUMAN)[:]
        losers = game.players.select(
            lambda p: p.rol in [PlayerRol.INFECTED, PlayerRol.ELIMINATED])[:]

    elif no_human_remains(game):
        reason = "No queda ningún Humano en la partida."
        winners = game.players.select(
            lambda p: p.rol in [PlayerRol.THE_THING, PlayerRol.INFECTED])[:]
        losers = game.players.select(
            lambda p: p.rol == PlayerRol.ELIMINATED)[:]

    elif the_thing_infected_everyone(game):
        reason = '''La Cosa ha logrado infectar a todos los demás jugadores
                    sin que haya sido eliminado ningún Humano de la partida.'''
        winners = game.players.select(
            lambda p: p.rol == PlayerRol.THE_THING)[:]
        losers = game.players.select(
            lambda p: p.rol != PlayerRol.THE_THING)[:]

    return GameResult(
        reason=reason,
        winners=[PlayerInfo.model_validate(p) for p in winners],
        losers=[PlayerInfo.model_validate(p) for p in losers]
    )


@db_session
def play_panic_card(game_name: str, play_info: PlayInformation):
    result = {"message": "Panic card played"}
    game = find_game_by_name(game_name)
    verify_player_in_game(play_info.player_id, game_name)
    player = find_player_by_id(play_info.player_id)
    card = find_card_by_id(play_info.card_id)
    verify_panic_card(card)
    verify_card_in_hand(player, card)

    players_not_eliminated = select(
        p for p in game.players if p.rol != PlayerRol.ELIMINATED).count()

    # Que quede entre nosotros
    if card.name == CardPanicName.JUST_BETWEEN_US:
        verify_player_in_game(play_info.objective_player_id, game_name)
        objective_player: Player = find_player_by_id(
            play_info.objective_player_id)
        verify_adjacent_players(play_info.player_id,
                                play_info.objective_player_id,
                                players_not_eliminated - 1)
        process_between_us_card(game, player, card)

    # Revelaciones
    if card.name == CardPanicName.REVELATIONS:
        process_revelations_card(game, player, card)

    # Cuerdas podridas
    if card.name == CardPanicName.ROTTEN_ROPES:
        pass

    # Uno, dos...
    if card.name == CardPanicName.ONE_TWO:
        pass

    # Tres, cuatro
    if card.name == CardPanicName.THREE_FOUR:
        pass

    # ¿Es aquí la fiesta?
    if card.name == CardPanicName.SO_THIS_IS_THE_PARTY:
        pass

    # Ups
    if card.name == CardPanicName.OOOPS:
        pass

    # Olvidadizo
    if card.name == CardPanicName.FORGETFUL:
        pass

    # Vuelta y vuelta
    if card.name == CardPanicName.ROUND_AND_ROUND:
        process_round_and_round_card(game, player, card)

    # ¿No podemos ser amigos?
    if card.name == CardPanicName.CANT_WE_BE_FRIENDS:
        pass

    # Cita a ciegas
    if card.name == CardPanicName.BLIND_DATE:
        process_blind_date_card(game, player, card)

    # ¡Sal de aquí!
    if card.name == CardPanicName.GETOUT_OF_HERE:
        verify_player_in_game(play_info.objective_player_id, game_name)
        objective_player: Player = find_player_by_id(
            play_info.objective_player_id)
        verify_player_not_in_quarentine(objective_player)
        process_getout_of_here_card(game, player, card, objective_player)

    return result


@db_session
def pass_card(play_info: PlayInformation):
    player: Player = find_player_by_id(play_info.player_id)
    objective_player: Player = find_player_by_id(play_info.objective_player_id)
    card: Card = find_card_by_id(play_info.card_id)

    objective_player.hand.add(card)
    player.hand.remove(card)


@db_session
def card_interchange_response(game_name: str, game_data: InterchangeInformationIn):
    game: Game = find_game_by_name(game_name)
    player: Player = find_player_by_id(game_data.objective_player_id)
    player_card: Card = Card[game_data.objective_card_id]

    next_player: Player = find_player_by_id(game_data.player_id)
    next_player_card: Card = Card[game_data.card_id]

    player.hand.remove(player_card)
    next_player.hand.remove(next_player_card)

    player.hand.add(next_player_card)
    next_player.hand.add(player_card)

    update_game_turn(game_name)


async def show_revelations_cards(game_name: str, player_id: int, game_data: ShowRevelationsCardsIn):
    if game_data.show_my_cards:
        json_msg = {
            "event": utils.Events.REVELATIONS_SHOW,
            "player_id": player_id
        }
        await player_connections.send_event_to_other_players_in_game(game_name, json_msg, player_id)
    if player_id != game_data.original_player_id:
        next_player_id = get_id_of_next_player_in_turn(game_name)
        json_msg = {
            "event": Events.REVELATIONS_CARD_PLAYED,
            "original_player_id": game_data.original_player_id
        }
        await player_connections.send_event_to(next_player_id, json_msg)


@db_session
def blind_date_interchange(game_name: str, game_data: IntentionExchangeInformationIn):
    game: Game = find_game_by_name(game_name)
    player: Player = find_player_by_id(game_data.player_id)
    player_card: Card = find_card_by_id(game_data.card_id)

    card_to_exchange = select(
        c for c in game.draw_deck if 2 <= c.id and c.id <= 88).first()
    if card_to_exchange:
        game.draw_deck.remove(card_to_exchange)
        game.draw_deck_order.remove(card_to_exchange.id)
    else:
        card_to_exchange = select(
            c for c in game.discard_deck if 2 <= c.id and c.id <= 88).first()
        if card_to_exchange:
            game.discard_deck.remove(card_to_exchange)
    if card_to_exchange and player_card:
        player.hand.remove(player_card)
        player.hand.add(card_to_exchange)
