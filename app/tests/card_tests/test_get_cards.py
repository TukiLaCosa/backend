from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Card
from app.routers.cards.schemas import *
from fastapi import status
from pony.orm import db_session

client = TestClient(app)

# Database functions
@db_session
def create_card_for_testing(id: int) -> Card:
    return Card(id=id, number=4, type="THE_THING", name="The Thing",
                description="You are the thing, infect or kill everyone")


@db_session
def cleanup_database() -> None:
    Card.select().delete()


# Test cases
def test_empty_get_cards():
    response = client.get("/cards")
    assert response.status_code == status.HTTP_200_OK, "El código de estado de la respuesta no es 200 (OK)."
    assert response.json() == [
    ], f"El mensaje de la respuesta no es []. El mensaje de la respuesta obtenido es {response.json()}."


def test_get_one_card(mocker):
    cleanup_database()
    create_card_for_testing(1)
    response = client.get("/cards")

    expected_response = [
        {
            "id": 1,
            "number": 4,
            "type": "THE_THING",
            "name": "The Thing",
            "description": "You are the thing, infect or kill everyone"
        }
    ]

    assert response.status_code == 200, f"El código de estado de la respuesta no es 200 (OK). El codigo de estado obtenido es {response.status_code}."
    assert response.json() == expected_response, "El mensaje de la respuesta no es el esperado."
    cleanup_database()
