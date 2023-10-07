from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_update_player():
    response = client.patch(
        '/players/1',
        json={'name': 'pepe'}
    )
    assert response.status_code == 200, "El código de estado de la respuesta no es 200 (OK)."
    assert response.json() == {
        'name': 'pepe',
        'id': 1,
        'position': -1
    }, "El contenido de la respuesta no coincide con los datos del jugador actualizado."


def test_update_inexistent_player():
    response = client.patch(
        '/players/99999999',
        json={'name': 'pepe'}
    )
    assert response.status_code == 404, "El código de estado de la respuesta no es 404 (Not Found)."


def test_update_player_bad_body():
    response = client.patch(
        '/players/1',
        json={'name': 7}
    )
    assert response.status_code == 422, "El código de estado de la respuesta no es 422 (Unprocessable Entity)."
