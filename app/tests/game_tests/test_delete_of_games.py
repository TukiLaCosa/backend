from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Game

client = TestClient(app)


class FakePlayer:
    def __init__(self, id, username, hand):
        self.id = id
        self.username = username
        self.hand = hand


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
        self.intention = None

    def delete(a):
        pass


ignacio = FakePlayer(1, "Ignacio", [])
anelio = FakePlayer(2, "Anelio", [])
ezequiel = FakePlayer(3, "Ezequiel", [])


games = [
    FakeGame(name="game1",
             players=[ignacio, anelio, ezequiel],
             host=ignacio,
             min_players=4,
             max_players=6,
             password=None,
             turn=-1,
             status="ENDED",
             round_direction="CLOCKWISE"
             )
]


def test_delete_game_success(mocker):
    mocker.patch.object(Game, "get", return_value=games[0])
    mocker.patch.object(FakeGame, "delete", return_value=None)

    response = client.delete("/games/game1")
    assert response.status_code == 200, "El código de estado de la respuesta no es 200 (OK)."
    assert response.json() == {
        "message": "Game deleted"}, "El mensaje de la respuesta no es 'Game deleted' (Juego eliminado)."


def test_delete_game_with_unstarted_status(mocker):
    game = FakeGame(name="game1",
                    players=[ignacio, anelio, ezequiel],
                    host=ignacio,
                    min_players=4,
                    max_players=6,
                    password=None,
                    turn=-1,
                    status="UNSTARTED",
                    round_direction="CLOCKWISE"
                    )
    mocker.patch.object(Game, "get", return_value=game)
    response = client.delete("/games/game2")
    assert response.status_code == 400, "El código de estado de la respuesta no es 400 (Bad Request)."


def test_delete_non_existing_game(mocker):
    mocker.patch.object(Game, "get", return_value=None)
    response = client.delete("/games/non_existing_game")
    assert response.status_code == 404,  "El código de estado de la respuesta no es 404 (Not Found)."
