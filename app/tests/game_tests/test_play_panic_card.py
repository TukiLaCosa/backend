from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Game, Player, Card, Intention
from pony.orm import db_session, select
from app.routers.games import utils as games_utils
from app.routers.players.utils import find_player_by_id
from app.routers.cards.schemas import CardType
import random

client = TestClient(app)


@db_session
def create_test_player(name: str):
    return Player(name=name)


@db_session
def create_test_game(name, min_players, max_players, password, host_player_id):
    game_data = {
        "name": name,
        "min_players": min_players,
        "max_players": max_players,
        "password": password,
        "host_player_id": host_player_id
    }
    return client.post("/games", json=game_data)


@db_session
def cleanup_database():
    Intention.select().delete()
    Game.select().delete()
    Player.select().delete()


@db_session
def replace_card_in_hand(game_name: str, player_id: int, card_id: int):
    games_utils.verify_player_in_game(player_id, game_name)
    game: Game = games_utils.find_game_by_name(game_name)
    player: Player = find_player_by_id(player_id)

    player_hand = list(player.hand)
    elegible_cards = [c for c in player_hand if c.type != CardType.THE_THING]
    if elegible_cards:
        random_card = random.choice(elegible_cards)

        card = select(c for c in Card if c.id == card_id).first()

        if card:
            player.hand.remove(random_card)
            player.hand.add(card)


def test_play_just_between_us_card():
    cleanup_database()
    card_to_play_id = 100
    players = []
    names = ["Ignacio", "Anelio", "Ezequiel",
             "Amparo", "Santiago", "Nehuen", "Gabriel"]
    for name in names:
        players.append(create_test_player(name=name))
    game = create_test_game(name="TestGame", min_players=7, max_players=7,
                            password="secret", host_player_id=players[0].id)
    for player in players[1:]:
        game_data = {
            "player_id": player.id,
            "password": "secret"
        }
        client.patch("/games/join/TestGame", json=game_data)
    init_response = client.patch(
        f"/games/TestGame/init?host_player_id={players[0].id}").json()
    for p in init_response['list_of_players']:
        if p['position'] == 0:
            player_id_turn = p['id']
        if p['position'] == 1:
            next_player_id = p['id']
    replace_card_in_hand(game_name='TestGame',
                         player_id=player_id_turn, card_id=card_to_play_id)
    game_data = {
        "card_id": card_to_play_id,
        "player_id": player_id_turn,
        "objective_player_id": next_player_id
    }
    response = client.post("/games/TestGame/play-panic-card", json=game_data)
    assert response.status_code == 200, "El codigo de estado de la respuesta no es 200 (OK)"

    cleanup_database()


def test_play_just_between_us_card():
    cleanup_database()
    card_to_play_id = 100
    players = []
    names = ["Ignacio", "Anelio", "Ezequiel",
             "Amparo", "Santiago", "Nehuen", "Gabriel"]
    for name in names:
        players.append(create_test_player(name=name))
    game = create_test_game(name="TestGame", min_players=7, max_players=7,
                            password="secret", host_player_id=players[0].id)
    for player in players[1:]:
        game_data = {
            "player_id": player.id,
            "password": "secret"
        }
        client.patch("/games/join/TestGame", json=game_data)
    init_response = client.patch(
        f"/games/TestGame/init?host_player_id={players[0].id}").json()
    for p in init_response['list_of_players']:
        if p['position'] == 0:
            player_id_turn = p['id']
        if p['position'] == 1:
            next_player_id = p['id']
    replace_card_in_hand(game_name='TestGame',
                         player_id=player_id_turn, card_id=card_to_play_id)
    game_data = {
        "card_id": card_to_play_id,
        "player_id": player_id_turn,
        "objective_player_id": next_player_id
    }
    response = client.post("/games/TestGame/play-panic-card", json=game_data)
    assert response.status_code == 200, "El codigo de estado de la respuesta no es 200 (OK)"

    cleanup_database()


def test_play_revelations_card():
    cleanup_database()
    card_to_play_id = 89
    players = []
    names = ["Ignacio", "Anelio", "Ezequiel", "Amparo",
             "Santiago", "Nehuen", "Gabriel", "Ignacio2"]
    for name in names:
        players.append(create_test_player(name=name))
    game = create_test_game(name="TestGame", min_players=7, max_players=7,
                            password="secret", host_player_id=players[0].id)
    for player in players[1:]:
        game_data = {
            "player_id": player.id,
            "password": "secret"
        }
        client.patch("/games/join/TestGame", json=game_data)
    init_response = client.patch(
        f"/games/TestGame/init?host_player_id={players[0].id}").json()
    for p in init_response['list_of_players']:
        if p['position'] == 0:
            player_id_turn = p['id']
        if p['position'] == 1:
            next_player_id = p['id']
    replace_card_in_hand(game_name='TestGame',
                         player_id=player_id_turn, card_id=card_to_play_id)
    game_data = {
        "card_id": card_to_play_id,
        "player_id": player_id_turn
    }
    response = client.post("/games/TestGame/play-panic-card", json=game_data)
    assert response.status_code == 200, "El codigo de estado de la respuesta no es 200 (OK)"

    cleanup_database()


def test_play_one_two_card():
    cleanup_database()
    card_to_play_id = 94
    players = []
    names = ["Ignacio", "Anelio", "Ezequiel", "Amparo",
             "Santiago", "Nehuen", "Gabriel", "Ignacio2"]
    for name in names:
        players.append(create_test_player(name=name))
    game = create_test_game(name="TestGame", min_players=7, max_players=7,
                            password="secret", host_player_id=players[0].id)
    for player in players[1:]:
        game_data = {
            "player_id": player.id,
            "password": "secret"
        }
        client.patch("/games/join/TestGame", json=game_data)
    init_response = client.patch(
        f"/games/TestGame/init?host_player_id={players[0].id}").json()
    for p in init_response['list_of_players']:
        if p['position'] == 0:
            player_id_turn = p['id']
        if p['position'] == 1:
            next_player_id = p['id']
    replace_card_in_hand(game_name='TestGame',
                         player_id=player_id_turn, card_id=card_to_play_id)
    game_data = {
        "card_id": card_to_play_id,
        "player_id": player_id_turn,
        "objective_player_id": next_player_id
    }
    response = client.post("/games/TestGame/play-panic-card", json=game_data)
    assert response.status_code == 200, "El codigo de estado de la respuesta no es 200 (OK)"

    cleanup_database()


def test_play_ooops_card():
    cleanup_database()
    card_to_play_id = 108
    players = []
    names = ["Ignacio", "Anelio", "Ezequiel", "Amparo", "Santiago",
             "Nehuen", "Gabriel", "Ignacio2", "Ignacio3", "Ignacio4"]
    for name in names:
        players.append(create_test_player(name=name))
    game = create_test_game(name="TestGame", min_players=10, max_players=10,
                            password="secret", host_player_id=players[0].id)
    for player in players[1:]:
        game_data = {
            "player_id": player.id,
            "password": "secret"
        }
        client.patch("/games/join/TestGame", json=game_data)
    init_response = client.patch(
        f"/games/TestGame/init?host_player_id={players[0].id}").json()
    for p in init_response['list_of_players']:
        if p['position'] == 0:
            player_id_turn = p['id']
        if p['position'] == 1:
            next_player_id = p['id']
    replace_card_in_hand(game_name='TestGame',
                         player_id=player_id_turn, card_id=card_to_play_id)
    game_data = {
        "card_id": card_to_play_id,
        "player_id": player_id_turn
    }
    response = client.post("/games/TestGame/play-panic-card", json=game_data)
    assert response.status_code == 200, "El codigo de estado de la respuesta no es 200 (OK)"

    cleanup_database()


def test_play_forgetful_card():
    cleanup_database()
    card_to_play_id = 93
    players = []
    names = ["Ignacio", "Anelio", "Ezequiel", "Amparo", "Santiago",
             "Nehuen", "Gabriel", "Ignacio2", "Ignacio3", "Ignacio4"]
    for name in names:
        players.append(create_test_player(name=name))
    game = create_test_game(name="TestGame", min_players=10, max_players=10,
                            password="secret", host_player_id=players[0].id)
    for player in players[1:]:
        game_data = {
            "player_id": player.id,
            "password": "secret"
        }
        client.patch("/games/join/TestGame", json=game_data)
    init_response = client.patch(
        f"/games/TestGame/init?host_player_id={players[0].id}").json()
    for p in init_response['list_of_players']:
        if p['position'] == 0:
            player_id_turn = p['id']
        if p['position'] == 1:
            next_player_id = p['id']
    replace_card_in_hand(game_name='TestGame',
                         player_id=player_id_turn, card_id=card_to_play_id)
    game_data = {
        "card_id": card_to_play_id,
        "player_id": player_id_turn
    }
    response = client.post("/games/TestGame/play-panic-card", json=game_data)
    assert response.status_code == 200, "El codigo de estado de la respuesta no es 200 (OK)"

    cleanup_database()


def test_play_round_and_round_card():
    cleanup_database()
    card_to_play_id = 102
    players = []
    names = ["Ignacio", "Anelio", "Ezequiel", "Amparo", "Santiago",
             "Nehuen", "Gabriel", "Ignacio2", "Ignacio3", "Ignacio4"]
    for name in names:
        players.append(create_test_player(name=name))
    game = create_test_game(name="TestGame", min_players=10, max_players=10,
                            password="secret", host_player_id=players[0].id)
    for player in players[1:]:
        game_data = {
            "player_id": player.id,
            "password": "secret"
        }
        client.patch("/games/join/TestGame", json=game_data)
    init_response = client.patch(
        f"/games/TestGame/init?host_player_id={players[0].id}").json()
    for p in init_response['list_of_players']:
        if p['position'] == 0:
            player_id_turn = p['id']
        if p['position'] == 1:
            next_player_id = p['id']
    replace_card_in_hand(game_name='TestGame',
                         player_id=player_id_turn, card_id=card_to_play_id)
    game_data = {
        "card_id": card_to_play_id,
        "player_id": player_id_turn
    }
    response = client.post("/games/TestGame/play-panic-card", json=game_data)
    assert response.status_code == 200, "El codigo de estado de la respuesta no es 200 (OK)"

    cleanup_database()


def test_play_blind_date_card():
    cleanup_database()
    card_to_play_id = 106
    players = []
    names = ["Ignacio", "Anelio", "Ezequiel", "Amparo", "Santiago",
             "Nehuen", "Gabriel", "Ignacio2", "Ignacio3", "Ignacio4"]
    for name in names:
        players.append(create_test_player(name=name))
    game = create_test_game(name="TestGame", min_players=10, max_players=10,
                            password="secret", host_player_id=players[0].id)
    for player in players[1:]:
        game_data = {
            "player_id": player.id,
            "password": "secret"
        }
        client.patch("/games/join/TestGame", json=game_data)
    init_response = client.patch(
        f"/games/TestGame/init?host_player_id={players[0].id}").json()
    for p in init_response['list_of_players']:
        if p['position'] == 0:
            player_id_turn = p['id']
        if p['position'] == 1:
            next_player_id = p['id']
    replace_card_in_hand(game_name='TestGame',
                         player_id=player_id_turn, card_id=card_to_play_id)
    player_hand = client.get(f"/players/{player_id_turn}/hand").json()
    for c in player_hand:
        if c["type"] != CardType.THE_THING and c["id"] != card_to_play_id:
            card_to_exchange_id = c["id"]
    game_data = {
        "card_id": card_to_play_id,
        "player_id": player_id_turn,
        "card_to_exchange_id": card_to_exchange_id
    }
    response = client.post("/games/TestGame/play-panic-card", json=game_data)
    assert response.status_code == 200, "El codigo de estado de la respuesta no es 200 (OK)"

    cleanup_database()


def test_play_getout_of_here_card():
    cleanup_database()
    card_to_play_id = 92
    players = []
    names = ["Ignacio", "Anelio", "Ezequiel", "Amparo", "Santiago",
             "Nehuen", "Gabriel", "Ignacio2", "Ignacio3", "Ignacio4"]
    for name in names:
        players.append(create_test_player(name=name))
    game = create_test_game(name="TestGame", min_players=10, max_players=10,
                            password="secret", host_player_id=players[0].id)
    for player in players[1:]:
        game_data = {
            "player_id": player.id,
            "password": "secret"
        }
        client.patch("/games/join/TestGame", json=game_data)
    init_response = client.patch(
        f"/games/TestGame/init?host_player_id={players[0].id}").json()
    for p in init_response['list_of_players']:
        if p['position'] == 0:
            player_id_turn = p['id']
        if p['position'] == 1:
            next_player_id = p['id']
    replace_card_in_hand(game_name='TestGame',
                         player_id=player_id_turn, card_id=card_to_play_id)
    game_data = {
        "card_id": card_to_play_id,
        "player_id": player_id_turn,
        "objective_player_id": next_player_id
    }
    response = client.post("/games/TestGame/play-panic-card", json=game_data)
    assert response.status_code == 200, "El codigo de estado de la respuesta no es 200 (OK)"

    cleanup_database()
