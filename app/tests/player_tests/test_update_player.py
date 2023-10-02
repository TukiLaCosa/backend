from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_update_player():
    response = client.patch(
        '/players/1',
        json={'name': 'pepe'}
    )
    assert response.status_code == 200
    assert response.json() == {
        'name': 'pepe',
        'id': 1,
        'position': -1
    }


def test_update_inexistent_player():
    response = client.patch(
        '/players/99999999',
        json={'name': 'pepe'}
    )
    assert response.status_code == 404


def test_update_player_bad_body():
    response = client.patch(
        '/players/1',
        json={'name': 7}
    )
    assert response.status_code == 422
