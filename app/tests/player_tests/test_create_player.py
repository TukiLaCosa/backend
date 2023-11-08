from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_player():
    response = client.post(
        '/players',
        json={'name': 'pepito'}
    )
    assert response.status_code == 200, "El código de estado de la respuesta no es 201 (Created)."
    assert response.json() == {
        'id': 1,
        'name': 'pepito',
    }, "El contenido de la respuesta no coincide con los datos del jugador creado."


def test_create_player_with_same_name():
    response = client.post(
        '/players',
        json={'name': 'pepito'}
    )
    assert response.status_code == 201, "El código de estado de la respuesta no es 201 (Created)."
    assert response.json() == {
        'id': 2,
        'name': 'pepito',
    }, "El contenido de la respuesta no coincide con los datos del jugador creado."


def test_create_player_bad_body():
    response = client.post(
        "/players",
        json={"bad": "body"},
    )
    assert response.status_code == 422, "El código de estado de la respuesta no es 422 (Unprocessable Entity)."


def test_create_player_bad_name():
    response = client.post(
        "/players",
        json={"name": 3},
    )
    assert response.status_code == 422, "El código de estado de la respuesta no es 422 (Unprocessable Entity)."


def test_create_player_short_name():
    response = client.post(
        "/players",
        json={"name": "a"},
    )
    assert response.status_code == 422, "El código de estado de la respuesta no es 422 (Unprocessable Entity)."


def test_create_player_large_name():
    response = client.post(
        "/players",
        json={"name": "a"*31},
    )
    assert response.status_code == 422, "El código de estado de la respuesta no es 422 (Unprocessable Entity)."
