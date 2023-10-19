from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Game, Player, Card
from app.routers.cards.schemas import *
from pony.orm import db_session
from fastapi import status

client = TestClient(app)


@db_session
def cleanup_database():
    Game.select().delete()
    Player.select().delete()
    Card.select().delete()


def test_create_cards_succesfully():
    cleanup_database()
    for i in range(4, 13):
        card_data = {
            "number": i,
            "type": 'THE_THING',
            "subtype": 'CONTAGION',
            "name": "The Thing",
            "description": "You are the thing, infect or kill everyone"
        }

        response = client.post("/cards", json=card_data)

        assert response.status_code == status.HTTP_201_CREATED, f"El código de estado de la respuesta no es 201 (Created). El código de estado obtenido es {response.status_code}."

        with db_session:
            created_card = Card.get(name=card_data["name"])
        assert created_card is not None

        assert response.json() == {
            "number": i,
            "type": "THE_THING",
            "subtype": "CONTAGION",
            "name": "The Thing",
            "description": "You are the thing, infect or kill everyone"
        }, "El contenido de la respuesta no coincide con los datos de la carta creada."
        cleanup_database()


def test_create_card_bad_body():
    cleanup_database()
    response = client.post(
        "/cards",
        json={"bad": "body"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es {response.status_code}."
    cleanup_database()


# Test card number
def test_create_card_missing_number():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "type": "THE_THING",
            "subtype": 'CONTAGION',
            "name": "The Thing",
            "description": "You are the thing, infect or kill everyone"
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()


def test_create_card_bad_number():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "number": "bad",
            "type": "THE_THING",
            "subtype": 'CONTAGION',
            "name": "The Thing",
            "description": "You are the thing, infect or kill everyone"
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()


def test_create_card_low_number():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "number": 3,
            "type": "THE_THING",
            "subtype": 'CONTAGION',
            "name": "The Thing",
            "description": "You are the thing, infect or kill everyone"
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()


def test_create_card_high_number():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "number": 13,
            "type": "THE_THING",
            "subtype": 'CONTAGION',
            "name": "The Thing",
            "description": "You are the thing, infect or kill everyone"
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()


#   Test card type
def test_create_card_missing_type():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "number": 4,
            "subtype": 'CONTAGION',
            "name": "The Thing",
            "name": "The Thing",
            "description": "You are the thing, infect or kill everyone"
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()


def test_create_card_bad_type():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "number": 4,
            "type": "THE_THIN",
            "subtype": 'CONTAGION',
            "name": "The Thing",
            "description": "You are the thing, infect or kill everyone"
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()

#   Test card names


def test_create_card_missing_name():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "number": 4,
            "type": "THE_THING",
            "subtype": 'CONTAGION',
            "description": "You are the thing, infect or kill everyone"
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()


def test_create_card_bad_name():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "number": 4,
            "type": "THE_THING",
            "subtype": 'CONTAGION',
            "name": 3,
            "description": "You are the thing, infect or kill everyone"
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()


def test_create_card_short_name():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "number": 4,
            "type": "THE_THING",
            "subtype": 'CONTAGION',
            "name": "a",
            "description": "You are the thing, infect or kill everyone"
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()


def test_create_card_large_name():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "number": 4,
            "type": "THE_THING",
            "subtype": 'CONTAGION',
            "name": "a"*51,
            "description": "You are the thing, infect or kill everyone"
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()


# Test card description
def test_create_card_missing_description():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "number": 4,
            "type": "THE_THING",
            "subtype": 'CONTAGION',
            "name": "The Thing"
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()


def test_create_card_bad_description():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "number": 4,
            "type": "THE_THING",
            "subtype": 'CONTAGION',
            "name": "The Thing",
            "description": 22
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()


def test_create_card_short_description():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "number": 4,
            "type": "THE_THING",
            "subtype": 'CONTAGION',
            "name": "The Thing",
            "description": "ee"
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()


def test_create_card_large_description():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "number": 4,
            "type": "THE_THING",
            "subtype": 'CONTAGION',
            "name": "The Thing",
            "description": "You are the thing, infect or kill everyone"*1000
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()


# Test card subtype
def test_create_card_missing_subtype():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "number": 4,
            "type": "THE_THING",
            "name": "The Thing",
            "description": "You are the thing, infect or kill everyone"
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()


def test_create_card_bad_subtype():
    cleanup_database()
    response = client.post(
        "/cards",
        json={
            "number": 4,
            "type": "THE_THING",
            "subtype": 'CONTAGIOOO',
            "name": "The Thing",
            "description": "You are the thing, infect or kill everyone"
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"El código de estado de la respuesta no es 422(Unprocessable Entity). El código obtenido es { response} "
    cleanup_database()
