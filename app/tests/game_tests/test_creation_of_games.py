from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Game, Player
from app.routers.games.schemas import GameCreationOut
from pony.orm import db_session
import pytest

client = TestClient(app)


@db_session
def create_test_player(name: str):
    return Player(name=name)


@db_session
def cleanup_database():
    Game.select().delete()
    Player.select().delete()


def test_create_successfull_game():
    cleanup_database()
    test_player = create_test_player("Ignacio")

    game_data = {
        "name": "TestGame",
        "min_players": 4,
        "max_players": 6,
        "password": "secret",
        "host_player_id": test_player.id
    }

    response = client.post("/games", json=game_data)

    assert response.status_code == 201

    with db_session:
        created_game = Game.get(name=game_data["name"])
    assert created_game is not None

    game_creation_response = GameCreationOut(**response.json())
    assert game_creation_response.name == game_data["name"]
    assert game_creation_response.status == "UNSTARTED"
    assert game_creation_response.min_players == game_data["min_players"]
    assert game_creation_response.max_players == game_data["max_players"]
    assert game_creation_response.is_private == True
    assert game_creation_response.host_player_id == test_player.id
    cleanup_database()


def test_create_without_player_in_ddbb():
    cleanup_database()
    game_data = {
        "name": "TestGame",
        "min_players": 4,
        "max_players": 6,
        "password": "secret",
        "host_player_id": 1
    }
    response = client.post("/games", json=game_data)
    assert response.status_code == 404
    cleanup_database()


def test_create_game_with_a_host_already_hosting():
    cleanup_database()
    test_player = create_test_player("Ignacio")
    game_data = {
        "name": "TestGame",
        "min_players": 4,
        "max_players": 6,
        "password": "secret",
        "host_player_id": test_player.id
    }
    for i in range(2):
        response = client.post("/games", json=game_data)
    assert response.status_code == 400
    cleanup_database()


def test_create_game_with_same_name():
    cleanup_database()
    test_player1 = create_test_player("Ignacio")
    test_player2 = create_test_player("Ezequiel")
    game_data = [
        {
            "name": "TestGame",
            "min_players": 4,
            "max_players": 6,
            "password": "secret",
            "host_player_id": test_player1.id
        }, {
            "name": "TestGame",
            "min_players": 4,
            "max_players": 6,
            "password": "secret",
            "host_player_id": test_player2.id
        }
    ]
    for i in game_data:
        response = client.post("/games", json=i)
    assert response.status_code == 400
    cleanup_database()
