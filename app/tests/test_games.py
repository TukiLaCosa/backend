from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class FakePlayer:
    def __init__(self, id, username):
        self.id = id
        self.username = username


ignacio = FakePlayer(1, "Ignacio")
anelio = FakePlayer(2, "Anelio")
ezequiel = FakePlayer(3, "Ezequiel")


class FakeQueryGame(object):
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


games = [
    FakeQueryGame(name="game1",
                  players=[ignacio, anelio, ezequiel],
                  host=ignacio,
                  min_players=4,
                  max_players=6,
                  password=None,
                  turn=-1,
                  status="UNSTARTED",
                  round_direction="CLOCKWISE"),
    FakeQueryGame(name="game2",
                  players=[anelio, ezequiel],
                  host=anelio,
                  min_players=4,
                  max_players=4,
                  password="MyPassword",
                  turn=-1,
                  status="UNSTARTED",
                  round_direction="CLOCKWISE"),
    FakeQueryGame(name="game3",
                  players=[ezequiel],
                  host=ezequiel,
                  min_players=12,
                  max_players=12,
                  password=None,
                  turn=-1,
                  status="UNSTARTED",
                  round_direction="CLOCKWISE")
]

bad_game_num_players = [
    FakeQueryGame(name="game4",
                  players=[ignacio],
                  host=ignacio,
                  min_players=3,
                  max_players=13,
                  password=None,
                  turn=-1,
                  status="UNSTARTED",
                  round_direction="CLOCKWISE")
]


def test_empty_get_games(mocker):
    mocker.patch("app.database.models.Game.select", return_value=[])
    response = client.get("/games")
    assert response.status_code == 200
    assert response.json() == []


def test_get_one_game(mocker):
    mocker.patch("app.database.models.Game.select", return_value=[games[0]])
    mocker.patch("app.database.models.Game.get", return_value=games[0])
    response = client.get("/games")
    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "game1",
            "min_players": 4,
            "max_players": 6,
            "host_player_id": 1,
            "status": "UNSTARTED",
            "is_private": False,
            "players_joined": 3
        }
    ]
