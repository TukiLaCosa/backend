from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Card
from app.routers.cards.schemas import *
from fastapi import status
from pony.orm import db_session

client = TestClient(app)


@db_session
def create_card_for_testing(id: int) -> Card:
    return Card(id=id, number=4, type="THE_THING", subtype="CONTAGION", name="The Thing",
                description="You are the thing, infect or kill everyone")


@db_session
def cleanup_database() -> None:
    Card.select().delete()


# Fake classes
class FakeCard:
    def __init__(self, id, number, type, subtype, name, description):
        self.id = id
        self.number = number
        self.type = type
        self.subtype = subtype
        self.name = name
        self.description = description

    def delete():
        pass


card = FakeCard(id=1, number=4, type="THE_THING", subtype="CONTAGION", name="The Thing",
                description="You are the thing, infect or kill everyone")


# Parametrized functions
def perform_a_valid_delete_test(card_id):
    response = client.delete(f"/cards/{card_id}")
    assert response.status_code == status.HTTP_200_OK, f"El código de estado de la respuesta no es 200 (OK). El codigo de estado obtenido es {response.status_code}."
    assert response.json() == {
        "message": "Card deleted"}, f"El mensaje de la respuesta no es el esperado. El mensaje de la respuesta obtenida es {response.json()}."


def perform_an_invalid_delete_test(card_id, expected_status_code):
    response = client.delete(f"/cards/{card_id}")
    assert response.status_code == expected_status_code, f"El código de estado de la respuesta no es {expected_status_code}. El codigo de estado obtenido es {response.status_code}."


# Test cases
def test_delete_card_succesfully(mocker):
    mocker.patch.object(Card, "get", return_value=card)
    mocker.patch.object(FakeCard, "delete", return_value=None)

    perform_a_valid_delete_test("1")


def test_delete_card_with_invalid_id(mocker):
    mocker.patch.object(Card, "get", return_value=card)

    perform_an_invalid_delete_test(
        "error", status.HTTP_422_UNPROCESSABLE_ENTITY)
    perform_an_invalid_delete_test("110", status.HTTP_400_BAD_REQUEST)
    perform_an_invalid_delete_test("0", status.HTTP_400_BAD_REQUEST)
    perform_an_invalid_delete_test("-4", status.HTTP_400_BAD_REQUEST)


def test_delete_non_existing_card(mocker):
    mocker.patch.object(Card, "get", return_value=None)

    perform_an_invalid_delete_test("4", status.HTTP_404_NOT_FOUND)


def test_delete_an_already_deleted_card():
    cleanup_database()
    create_card_for_testing(1)

    response = client.delete("/cards/1")
    assert response.status_code == status.HTTP_200_OK, f"En la primer eliminación, el código de estado de la respuesta esperado es 200 (OK). El código de estado de la respuesta obtenida es {response.status_code}."
    assert response.json() == {
        "message": "Card deleted"}, f"En la primer eliminación, el mensaje de la respuesta no es el esperado. El mensaje de la respuesta obtenida es {response.json()}."

    perform_an_invalid_delete_test("1", status.HTTP_404_NOT_FOUND)
    cleanup_database()
