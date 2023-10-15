from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Card
from app.routers.cards.schemas import *
from fastapi import status
from pony.orm import db_session

client = TestClient(app)


@db_session
def create_card_for_testing(id: int) -> Card:
    return Card(id=id, number=4, type="THE_THING", name="The Thing",
                description="You are the thing, infect or kill everyone")


@db_session
def cleanup_database() -> None:
    Card.select().delete()


# Parametrized functions
def perform_a_valid_update_test(card_id, success_request_data):
    response = client.patch(f"/cards/{card_id}", json=success_request_data)

    assert response.status_code == status.HTTP_200_OK, f"El código de estado de la respuesta no es 200 (OK). El codigo de estado obtenido es {response.status_code}."
    assert response.json() == {
        "number": 10,
        "type": "PANIC",
        "name": "PANIC",
        "description": "PANIC",
    }, "El contenido de la respuesta no coincide con los datos actualizados."


def perform_an_invalid_update_test(card_id, expected_status_code, json_data):
    response = client.patch(f"/cards/{card_id}", json=json_data)
    assert response.status_code == expected_status_code, f"El código de estado de la respuesta no es {expected_status_code}. El codigo de estado obtenido es {response.status_code}."


# Test cases
def test_patch_card_succesfully():
    cleanup_database()
    create_card_for_testing(1)
    success_request_data = {
        "number": 10,
        "type": "PANIC",
        "name": "PANIC",
        "description": "PANIC"
    }

    perform_a_valid_update_test("1", success_request_data)
    cleanup_database()


def test_patch_card_greater_number():
    cleanup_database()
    create_card_for_testing(1)

    greater_number_request_data = {
        "number": 13,
        "type": "PANIC",
        "name": "PANIC",
        "description": "PANIC"
    }
    perform_an_invalid_update_test(
        "1", status.HTTP_422_UNPROCESSABLE_ENTITY, greater_number_request_data)
    cleanup_database()


def test_patch_card_lower_number():
    cleanup_database
    lower_number_request_data = {
        "number": 2,
        "type": "PANIC",
        "name": "PANIC",
        "description": "PANIC"
    }
    perform_an_invalid_update_test(
        "1", status.HTTP_422_UNPROCESSABLE_ENTITY, lower_number_request_data)
    cleanup_database()


def test_patch_card_invalid_number():
    cleanup_database()
    invalid_number_request_data = {
        "number": "error",
        "type": "PANIC",
        "name": "PANIC",
        "description": "PANIC"
    }
    perform_an_invalid_update_test(
        "1", status.HTTP_422_UNPROCESSABLE_ENTITY, invalid_number_request_data)
    cleanup_database()


def test_patch_card_invalid_type():
    cleanup_database()

    create_card_for_testing(1)

    invalid_type_request_data = {
        "number": 4,
        "type": "error",
        "name": "PANIC",
        "description": "PANIC"
    }
    perform_an_invalid_update_test(
        "1", status.HTTP_422_UNPROCESSABLE_ENTITY, invalid_type_request_data)

    cleanup_database()


def test_patch_card_invalid_name():
    cleanup_database()

    create_card_for_testing(1)

    invalid_name_request_data = {
        "number": 4,
        "type": "PANIC",
        "name": 123,
        "description": "PANIC"
    }
    perform_an_invalid_update_test(
        "1", status.HTTP_422_UNPROCESSABLE_ENTITY, invalid_name_request_data)

    cleanup_database()


def test_patch_card_short_name():
    cleanup_database()

    create_card_for_testing(1)

    short_name_request_data = {
        "number": 4,
        "type": "PANIC",
        "name": "P",
        "description": "PANIC"
    }
    perform_an_invalid_update_test(
        "1", status.HTTP_422_UNPROCESSABLE_ENTITY, short_name_request_data)

    cleanup_database()


def test_patch_card_long_name():
    cleanup_database()

    create_card_for_testing(1)

    long_name_request_data = {
        "number": 4,
        "name": "PANIC"*100,
        "description": "PANIC"
    }
    perform_an_invalid_update_test(
        "1", status.HTTP_422_UNPROCESSABLE_ENTITY, long_name_request_data)

    cleanup_database()


def test_patch_card_invalid_description():
    cleanup_database()

    create_card_for_testing(1)

    invalid_description_request_data = {
        "number": 4,
        "type": "PANIC",
        "name": "PANIC",
        "description": 123
    }
    perform_an_invalid_update_test(
        "1", status.HTTP_422_UNPROCESSABLE_ENTITY, invalid_description_request_data)

    cleanup_database()


def test_patch_card_short_description():
    cleanup_database()

    create_card_for_testing(1)

    short_description_request_data = {
        "number": 4,
        "type": "PANIC",
        "name": "PANIC",
        "description": "P"
    }
    perform_an_invalid_update_test(
        "1", status.HTTP_422_UNPROCESSABLE_ENTITY, short_description_request_data)

    cleanup_database()


def test_patch_card_long_description():
    cleanup_database()

    create_card_for_testing(1)

    long_description_request_data = {
        "number": 4,
        "type": "PANIC",
        "name": "PANIC",
        "description": "PANIC"*1000
    }
    perform_an_invalid_update_test(
        "1", status.HTTP_422_UNPROCESSABLE_ENTITY, long_description_request_data)

    cleanup_database()
