from fastapi.testclient import TestClient
from app.main import app
from app.database.models import *
from app.routers.cards.schemas import *
from fastapi import status
from pony.orm import db_session
from app.routers.cards.utils import *


client = TestClient(app)


@db_session
def mock_data() -> CardResponse:
    Card(id=1, number=4, type='THE_THING',
         subtype='CONTAGION',
         name="The Thing",
         description="You are the thing, infect or kill everyone"
         )

    card = Card.get(id=1)
    return card


@db_session
def delete_mock_data(id: int):
    Card.get(id=id).delete()


@db_session
def action_mock_data() -> Card:
    return (Card(id=2, number=4, type=CardType.STAY_AWAY, subtype=CardSubtype.ACTION, name="Action Card",
                 description="This is an action card"))


def test_find_card_by_id_success():
    mock_response = mock_data()
    response = find_card_by_id(mock_response.id)
    try:
        assert mock_response.id == response.id, "Find card by id failed"
    finally:
        delete_mock_data(mock_response.id)


def test_find_card_by_id_fail():
    card_id = 109
    client.delete(f'/cards/{card_id}')

    try:
        find_card_by_id(card_id)
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND, f"El status code obtenido es {e.status_code} y debería ser {status.HTTP_404_NOT_FOUND}"
        assert e.detail == f"Card not found", f"El detalle obtenido es {e.detail} y debería ser 'Card not found.'"


@db_session
def test_verify_action_card_success():
    card = action_mock_data()
    try:
        verify_action_card(card)
    except HTTPException as e:
        assert False, f"Unexpected HTTPException: {e}"
    finally:
        card.delete()


@db_session
def test_verify_action_card_failure():
    card = Card(id=1, number=4, type="PANIC", subtype=CardSubtype.PANIC, name="Panic Card",
                description="This is a panic card")
    try:
        verify_action_card(card)
        assert False, "Expected HTTPException not raised"
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST, f"El status code obtenido es {e.status_code} y debería ser {status.HTTP_400_BAD_REQUEST}"
    finally:
        card.delete()


@db_session
def test_get_card_name_by_id_success():
    # Create a test card
    card = Card(id=1, number=4, type="PANIC", subtype=CardSubtype.PANIC, name="Test Card",
                description="This is a panic card")

    # Call the function with the test card's ID
    result = get_card_name_by_id(card.id)
    card.delete()

    # Check that the result matches the test card's name
    assert result == "Test Card", f"Error: The function did not return the correct card name ('Test Card'). Instead, it returned ({ result })."


@db_session
def test_get_card_type_by_id_success():
    # Create a test card
    card = Card(id=1, number=4, type="PANIC", subtype=CardSubtype.PANIC, name="Test Card",
                description="This is a panic card")

    # Call the function with the card's ID
    card_type = get_card_type_by_id(card.id)
    card.delete()

    # Check that the returned type matches the card's type
    assert card_type == "PANIC", f"Error: The function did not return the correct card type. Instead, it returned ({ card_type })."


@db_session
def test_is_flamethrower_success():
    # Create a test card
    card = Card(id=1, number=4, type=CardType.STAY_AWAY, subtype=CardSubtype.ACTION, name=CardActionName.FLAMETHROWER,
                description="This is a panic card")

    # Call the function with the card's ID
    response = is_flamethrower(card.id)
    card.delete()

    # Check that the returned type matches the card's type
    assert response, f"Error: The function returned {response} instead of True."


@db_session
def test_is_whisky_success():
    # Create a test card
    card = Card(id=1, number=4, type=CardType.STAY_AWAY, subtype=CardSubtype.ACTION, name=CardActionName.WHISKEY,
                description="This is a WHISKEY card")

    # Call the function with the card's ID
    response = is_whiskey(card.id)
    card.delete()

    # Check that the returned type matches the card's type
    assert response, f"Error: The function returned {response} instead of True."
