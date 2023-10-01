from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Game, Player
from app.routers.games.schemas import GameInformationOut
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
    client.post("/games", json=game_data)


@db_session
def cleanup_database():
    Game.select().delete()
    Player.select().delete()


def test_join_player_succesfully():
    cleanup_database()
    test_player1 = create_test_player("Ignacio")
    test_player2 = create_test_player("Anelio")
    create_test_game(name="TestGame", min_players=4, max_players=6,
                     password="secret", host_player_id=test_player1.id)
    game_data = {
        "player_id": test_player2.id,
        "password": "secret"
    }

    response = client.patch("/games/join/TestGame", json=game_data)

    assert response.status_code == 200

    game_join_response = GameInformationOut(**response.json())
    assert game_join_response.name == "TestGame"
    assert game_join_response.status == "UNSTARTED"
    assert game_join_response.min_players == 4
    assert game_join_response.max_players == 6
    assert game_join_response.is_private == True
    assert game_join_response.num_of_players == 2

    cleanup_database()


def test_join_game_not_found():
    cleanup_database()
    test_player = create_test_player("Ignacio")
    game_data = {
        "player_id": test_player.id,
        "password": "secret"
    }
    response = client.patch("/games/join/TestGame", json=game_data)
    assert response.status_code == 404
    cleanup_database()


def test_join_game_player_not_found():
    cleanup_database()
    test_player1 = create_test_player("Ignacio")
    test_player2 = create_test_player("Ezequiel")
    create_test_game(name="TestGame", min_players=4, max_players=6,
                     password="secret", host_player_id=test_player1.id)
    game_data = {
        "player_id": test_player2.id + 1,
        "password": "secret"
    }
    response = client.patch("/games/join/TestGame", json=game_data)
    assert response.status_code == 404
    cleanup_database()


def test_join_game_player_already_in_game():
    cleanup_database()
    test_player1 = create_test_player("Ignacio")
    test_player2 = create_test_player("Ezequiel")
    create_test_game(name="TestGame", min_players=4, max_players=6,
                     password="secret", host_player_id=test_player1.id)
    game_data = {
        "player_id": test_player2.id,
        "password": "secret"
    }
    for i in range(2):
        response = client.patch("/games/join/TestGame", json=game_data)
    assert response.status_code == 400
    cleanup_database()


def test_join_game_full_of_players():
    cleanup_database()
    test_player1 = create_test_player("Ignacio")
    test_player2 = create_test_player("Ezequiel")
    test_player3 = create_test_player("Anelio")
    test_player4 = create_test_player("Amparo")
    test_player5 = create_test_player("Nehuen")
    list_of_players = [test_player2, test_player3, test_player4, test_player5]
    create_test_game(name="TestGame", min_players=4, max_players=4,
                     password="secret", host_player_id=test_player1.id)
    for player in list_of_players:
        game_data = {
            "player_id": player.id,
            "password": "secret"
        }
        response = client.patch("/games/join/TestGame", json=game_data)
    assert response.status_code == 400
    cleanup_database()


def test_join_game_with_invalid_password():
    cleanup_database()
    test_player1 = create_test_player("Ignacio")
    test_player2 = create_test_player("Ezequiel")
    create_test_game(name="TestGame", min_players=4, max_players=6,
                     password="secret", host_player_id=test_player1.id)
    game_data = {
        "player_id": test_player2.id,
        "password": "wrong_password"
    }
    response = client.patch("/games/join/TestGame", json=game_data)
    assert response.status_code == 400
    cleanup_database()


def test_join_game_with_player_in_another_game():
    cleanup_database()
    test_player1 = create_test_player("Ignacio")
    test_player2 = create_test_player("Ezequiel")
    test_player3 = create_test_player("Anelio")
    create_test_game(name="TestGame1", min_players=4, max_players=6,
                     password="secret", host_player_id=test_player1.id)
    create_test_game(name="TestGame2", min_players=4, max_players=6,
                     password="secret", host_player_id=test_player2.id)
    game_data = {
        "player_id": test_player3.id,
        "password": "secret"
    }
    client.patch("/games/join/TestGame1", json=game_data)
    response = client.patch("/games/join/TestGame2", json=game_data)
    assert response.status_code == 400
    cleanup_database()
