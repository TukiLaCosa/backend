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


def test_empty_get_games(mocker):
    mocker.patch.object(Game, "select", return_value=[])
    response = client.get("/games")
    assert response.status_code == 200, "El código de estado de la respuesta no es 200 (OK)."
    assert response.json() == [], "El contenido de la respuesta no está vacío como se esperaba."


def test_get_one_game(mocker):
    mocker.patch.object(Game, "select", return_value=[games[0]])
    response = client.get("/games")
    assert response.status_code == 200, "El código de estado de la respuesta no es 200 (OK)."
    assert response.json() == [
        {
            "name": "game1",
            "min_players": 4,
            "max_players": 6,
            "host_player_id": 1,
            "status": "UNSTARTED",
            "is_private": False,
            "num_of_players": 3
        }
    ], "El contenido de la respuesta no coincide con el juego esperado."
