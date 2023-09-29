from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Game

client = TestClient(app)


class FakePlayer:
    def __init__(self, id, username):
        self.id = id
        self.username = username


class FakeGame:
    def __init__(
            self,
            name,
            players,
            host,
            min_players,
            max_players,
            password,
            turn,
            status,
            round_direction
    ):
        self.name = name
        self.players = players
        self.host = host
        self.min_players = min_players
        self.max_players = max_players
        self.password = password
        self.turn = turn
        self.status = status
        self.round_direction = round_direction


ignacio = FakePlayer(1, "Ignacio")
anelio = FakePlayer(2, "Anelio")
ezequiel = FakePlayer(3, "Ezequiel")


games = [
    FakeGame(name="game1",
             players=[ignacio, anelio, ezequiel],
             host=ignacio,
             min_players=4,
             max_players=6,
             password=None,
             turn=-1,
             status="UNSTARTED",
             round_direction="CLOCKWISE"
             )
]


def test_update_game_successful(mocker):
    mocker.patch.object(Game, "get", return_value=games[0])
    request_data = {
        "min_players": 5,
        "max_players": 7,
        "password": "new_password"
    }

    response = client.patch("games/game1", json=request_data)
    assert response.status_code == 200
    assert response.json() == {
        "name": "game1",
        "min_players": 5,
        "max_players": 7,
        "is_private": True,
        "status": "UNSTARTED"
    }


def test_update_non_existing_game(mocker):
    mocker.patch.object(Game, "get", return_value=None)
    request_data = {
        "min_players": 5,
        "max_players": 7,
        "password": "new_password"
    }
    response = client.patch("/games/non_existing_game", json=request_data)
    assert response.status_code == 404


def test_update_game_with_wrong_name(mocker):
    mocker.patch.object(Game, "get", return_value=games[0])
    request_data = {
        "min_players": 5,
        "max_players": 7,
        "password": "new_password"
    }
    response = client.patch("/games/wrong_game_name", json=request_data)
    assert response.status_code == 400
