from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Game, Player
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


def test_leave_game_successfully():
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
    response = client.patch(
        f"/games/leave/TestGame?player_id={players[2].id}")
    assert response.status_code == 200, "El codigo de estado de la respuesta no es 200 (OK)"
    cleanup_database()


def test_leave_inexistent_game():
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
    response = client.patch(
        f"/games/leave/BadGameName?player_id={players[2].id}")
    assert response.status_code == 404, "El codigo de estado de la respuesta no es 404 (Not Found)"
    cleanup_database()


def test_leave_game_not_in_unstarted_state():
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
    
    # Change to STARTED status
    client.patch(f"/games/TestGame/init?host_player_id={players[0].id}")
    response = client.patch(
        f"/games/leave/TestGame?player_id={players[2].id}")
    assert response.status_code == 400, "El codigo de estado de la respuesta no es 400 (Bad Request)"
    cleanup_database()


def test_leave_game_with_bad_player_id():
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
    response = client.patch(
        f"/games/leave/TestGame?player_id={players[1].id * 7}")
    assert response.status_code == 404, "El codigo de estado de la respuesta no es 404 (Not Found)"
    cleanup_database()


def test_leave_game_twice():
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
    client.patch(f"/games/leave/TestGame?player_id={players[2].id}")
    response = client.patch(f"/games/leave/TestGame?player_id={players[2].id}")
    assert response.status_code == 400, "El codigo de estado de la respuesta no es 400 (Bad Request)"
    cleanup_database()