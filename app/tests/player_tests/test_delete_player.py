from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_delete_player():
    response = client.delete(
        '/players/2',
    )
    assert response.status_code == 204


def test_delete_player_idempotent():
    response = client.delete(
        '/players/2',
    )
    assert response.status_code == 404


def test_delete_inexistent_player():
    response = client.delete(
        '/players/999999',
    )
    assert response.status_code == 404


def test_delete_player_bad_id():
    response = client.delete(
        '/players/badid',
    )
    assert response.status_code == 422
