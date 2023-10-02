from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_player():
    response = client.get(
        '/players/1',
    )
    assert response.status_code == 200
    assert response.json() == {
        'name': 'pepito',
        'id': 1,
        'position': -1
    }


def test_read_players():
    response = client.get(
        '/players',
    )
    assert response.status_code == 200
    assert response.json() == [{
        'name': 'pepito',
        'id': 1,
        'position': -1
    }]


def test_read_inexistent_player():
    response = client.get(
        '/players/9999999',
    )
    assert response.status_code == 404


def test_read_player_bad_id():
    response = client.get(
        '/players/a',
    )
    assert response.status_code == 422
