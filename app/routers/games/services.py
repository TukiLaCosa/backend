from pony.orm import *
from app.database.models import Game, Player, Card
from .schemas import *
from ..players.schemas import PlayerRol
from fastapi import HTTPException, status
from .utils import *
from ..cards import services as cards_services
from ..cards.utils import find_card_by_id, verify_action_card
from ..players.utils import find_player_by_id, verify_card_in_hand
from ..cards.schemas import CardActionName, CardResponse
from ..players.schemas import PlayerRol
import random


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
    game = Game.get(name=game_name)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    if game_name != game.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid game name")

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

    return GameStartOut(
        list_of_players=game.players,
        status=game.status,
        top_card_face=list(game.draw_deck)[0].type
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
def discard_card(game_name: str, game_data: DiscardInformationIn):
    game = Game.get(name=game_name)
    player = Player.get(id=game_data.player_id)
    card = Card.get(id=game_data.card_id)
    if card in player.hand:
        player.hand.remove(card)
    if game and card:
        game.discard_deck.add(card)


@db_session
def finish_game(name: str) -> Game:
    game: Game = find_game_by_name(name)

    try:
        verify_game_can_be_finished(game)
        game.status = GameStatus.ENDED
        # enviar por ws los resultados

        return game
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@db_session
def play_action_card(game_name: str, play_info: PlayInformation):
    result = {"message": "Action card played"}
    game = find_game_by_name(game_name)
    verify_player_in_game(play_info.player_id, game_name)
    player = find_player_by_id(play_info.player_id)
    card = find_card_by_id(play_info.card_id)
    verify_action_card(card)
    verify_card_in_hand(player, card)

    # Lanzallamas
    if card.name == CardActionName.FLAMETHROWER:
        verify_player_in_game(play_info.objective_player_id, game_name)
        players_not_eliminated = select(
            p for p in game.players if p.rol != PlayerRol.ELIMINATED).count()
        verify_adjacent_players(play_info.player_id,
                                play_info.objective_player_id,
                                players_not_eliminated - 1)
        objective_player = find_player_by_id(play_info.objective_player_id)
        objective_player.rol = PlayerRol.ELIMINATED

        # Las cartas del jugador eliminado van al mazo de descarte salvo sea carta la Cosa
        for card in objective_player.hand:
            if card.type != CardType.THE_THING:
                game.discard_deck.add(card)

        # Reacomodo las posiciones
        for player in game.players:
            if player.position > objective_player.position:
                player.position -= 1

        objective_player.position = -1

        game.discard_deck.add(card)
        player.hand.remove(card)

    # Analisis
    if card.name == CardActionName.ANALYSIS:
        verify_player_in_game(play_info.objective_player_id, game_name)
        players_not_eliminated = select(
            p for p in game.players if p.rol != PlayerRol.ELIMINATED).count()
        verify_adjacent_players(play_info.player_id,
                                play_info.objective_player_id,
                                players_not_eliminated - 1)
        objective_player = find_player_by_id(play_info.objective_player_id)

        # Armo listado de cartas del jugador objetivo para enviar en el body response
        result = [CardResponse(id=card.id,
                               number=card.number,
                               type=card.type,
                               subtype=card.subtype,
                               name=card.name,
                               description=card.description
                               ) for card in objective_player.hand]

        game.discard_deck.add(card)
        player.hand.remove(card)

    # Hacha
    if card.name == CardActionName.AXE:
        pass

    # Sospecha
    if card.name == CardActionName.SUSPICIOUS:
        verify_player_in_game(play_info.objective_player_id, game_name)
        players_not_eliminated = select(
            p for p in game.players if p.rol != PlayerRol.ELIMINATED).count()
        verify_adjacent_players(play_info.player_id,
                                play_info.objective_player_id,
                                players_not_eliminated - 1)
        objective_player = find_player_by_id(play_info.objective_player_id)

        # Elijo una carta al azar del jugador objetivo y armo el body response
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

    # Whisky
    if card.name == CardActionName.WHISKEY:
        pass

    # Determinacion
    if card.name == CardActionName.RESOLUTE:
        pass

    # Vigila tus espaldas
    if card.name == CardActionName.WATCH_YOUR_BACK:
        # Cambio direccion de la ronda
        if game.round_direction == RoundDirection.CLOCKWISE:
            game.round_direction = RoundDirection.COUNTERCLOCKWISE
        else:
            game.round_direction = RoundDirection.CLOCKWISE

        game.discard_deck.add(card)
        player.hand.remove(card)

    # Cambio de lugar
    if card.name == CardActionName.CHANGE_PLACES:
        verify_player_in_game(play_info.objective_player_id, game_name)
        players_not_eliminated = select(
            p for p in game.players if p.rol != PlayerRol.ELIMINATED).count()
        verify_adjacent_players(play_info.player_id,
                                play_info.objective_player_id,
                                players_not_eliminated - 1)
        objective_player = find_player_by_id(play_info.objective_player_id)

        # Intercambio de posiciones entre los jugadores
        tempPosition = player.position
        player.position = objective_player.position
        objective_player.position = tempPosition

        game.discard_deck.add(card)
        player.hand.remove(card)

    # Mas vale que corras
    if card.name == CardActionName.BETTER_RUN:
        verify_player_in_game(play_info.objective_player_id, game_name)
        objective_player = find_player_by_id(play_info.objective_player_id)

        # Intercambio de posiciones entre los jugadores
        tempPosition = player.position
        player.position = objective_player.position
        objective_player.position = tempPosition

        game.discard_deck.add(card)
        player.hand.remove(card)

    # Seduccion (Ojo porque esta carta modifica la mano del jugador objetivo)
    if card.name == CardActionName.SEDUCTION:
        verify_player_in_game(play_info.objective_player_id, game_name)
        objective_player = find_player_by_id(play_info.objective_player_id)
        objective_player_hand_list = list(objective_player.hand)
        eligible_cards = [
            card for card in objective_player_hand_list if card.type != CardType.THE_THING]
        random_card = random.choice(eligible_cards)

        player.hand.add(random_card)
        player.hand.remove(card)
        objective_player.hand.remove(random_card)
        objective_player.hand.add(card)

    return result
