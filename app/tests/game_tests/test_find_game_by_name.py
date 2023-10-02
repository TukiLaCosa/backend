from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Game, Player
from pony.orm import db_session
from app.routers.games.services import find_game_by_name

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


def test_find_game_successfully():
    cleanup_database()
    test_player = create_test_player("Ignacio")
    create_test_game(name="TestGame", min_players=4, max_players=6,
                     password="secret", host_player_id=test_player.id)
    response = find_game_by_name("TestGame")
    assert response.name == "TestGame"
    assert response.min_players == 4
    assert response.max_players == 6
    assert response.password == "secret"
    cleanup_database()
