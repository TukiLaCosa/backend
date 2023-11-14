from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Game, Player, Card
from pony.orm import db_session

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
    Game.select().delete()
    Player.select().delete()


def test_discard_card_successfully():
    cleanup_database()
    players = []
    names = ["Ignacio", "Anelio", "Ezequiel", "Amparo"]
    for name in names:
        players.append(create_test_player(name=name))
    game = create_test_game(name="TestGame", min_players=4, max_players=4,
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
            break
    player_hand = client.get(f"/players/{player_id_turn}/hand").json()
    for c in player_hand:
        if c['type'] != "THE_THING":
            game_data = {
                "player_id": player_id_turn,
                "card_id": c['id']
            }
            response = client.patch("/games/TestGame/discard", json=game_data)
            break
    assert response.status_code == 200, "El codigo de estado de la respuesta no es 200 (OK)"
    cleanup_database()


def test_discard_card_for_inexistent_game():
    cleanup_database()
    players = []
    names = ["Ignacio", "Anelio", "Ezequiel", "Amparo"]
    for name in names:
        players.append(create_test_player(name=name))
    game = create_test_game(name="TestGame", min_players=4, max_players=4,
                            password="secret", host_player_id=players[0].id)
    for player in players[1:]:
        game_data = {
            "player_id": player.id,
            "password": "secret"
        }
        client.patch("/games/join/TestGame", json=game_data)
    client.patch(f"/games/TestGame/init?host_player_id={players[0].id}")
    game_data = {
        "player_id": players[0].id,
        "card_id": 4
    }
    response = client.patch("/games/BadGame/discard", json=game_data)
    assert response.status_code == 404, "El codigo de estado de la respuesta no es 404 (NOT FOUND)"
    cleanup_database()


def test_discard_card_for_inexistent_player():
    cleanup_database()
    players = []
    names = ["Ignacio", "Anelio", "Ezequiel", "Amparo"]
    for name in names:
        players.append(create_test_player(name=name))
    game = create_test_game(name="TestGame", min_players=4, max_players=4,
                            password="secret", host_player_id=players[0].id)
    for player in players[1:]:
        game_data = {
            "player_id": player.id,
            "password": "secret"
        }
        client.patch("/games/join/TestGame", json=game_data)
    client.patch(f"/games/TestGame/init?host_player_id={players[0].id}")
    game_data = {
        "player_id": 123,
        "card_id": 4
    }
    response = client.patch("/games/TestGame/discard", json=game_data)
    assert response.status_code == 404, "El codigo de estado de la respuesta no es 404 (NOT FOUND)"
    cleanup_database()


def test_discard_card_for_inexistent_card():
    cleanup_database()
    players = []
    names = ["Ignacio", "Anelio", "Ezequiel", "Amparo"]
    for name in names:
        players.append(create_test_player(name=name))
    game = create_test_game(name="TestGame", min_players=4, max_players=4,
                            password="secret", host_player_id=players[0].id)
    for player in players[1:]:
        game_data = {
            "player_id": player.id,
            "password": "secret"
        }
        client.patch("/games/join/TestGame", json=game_data)
    client.patch(f"/games/TestGame/init?host_player_id={players[0].id}")
    game_data = {
        "player_id": players[0].id,
        "card_id": 123
    }
    response = client.patch("/games/TestGame/discard", json=game_data)
    assert response.status_code == 404, "El codigo de estado de la respuesta no es 404 (NOT FOUND)"
    cleanup_database()
