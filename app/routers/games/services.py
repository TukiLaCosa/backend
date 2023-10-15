from pony.orm import *
from app.database.models import Game, Player, Card
from .schemas import *
from fastapi import HTTPException, status
from .utils import find_game_by_name, list_of_unstarted_games
from ..cards import services as cards_services


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

    # setting the position of the players
    for idx, player in enumerate(game.players):
        player.position = idx

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
