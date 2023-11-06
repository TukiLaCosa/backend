from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Card, Player
from app.routers.players.utils import *
from pony.orm import *

client = TestClient(app)


def create_test_player():
    response = client.post(
        '/players',
        json={'name': 'pepito'}
    )
    player_id = response.json()['id']
    return player_id


def test_find_player_by_id_succes():
    # Create a player to find
    player_id = create_test_player()
    try:
        # Call the function being tested
        player = find_player_by_id(player_id)

        # Check that the returned player has the correct id and name
        assert player.id == player_id, "El id del jugador retornado no coincide con el id del jugador creado."
        assert player.name == 'pepito', "El nombre del jugador retornado no coincide con el nombre del jugador creado."
    except HTTPException as e:
        assert False, f"Se lanzó la excepción {e.status_code}. {e.detail}"
    finally:
        # Delete the player created
        client.delete(f'/players/{player_id}')


def test_get_player_name_by_id_succes():
    # Create a player to find
    player_id = create_test_player()

    # Call the function being tested
    try:
        player_name = get_player_name_by_id(player_id)

        assert player_name == 'pepito', "El nombre del jugador retornado no coincide con el nombre del jugador creado."
    except HTTPException as e:
        assert False, f"Se lanzó la excepción {e.status_code}. {e.detail}"
    finally:
        # Delete the player created
        client.delete(f'/players/{player_id}')


def test_find_player_by_id_fail():
    response = client.post(
        '/players',
        json={'name': 'pepito'}
    )
    player_id = response.json()['id']
    client.delete(f'/players/{player_id}')
    try:
        find_player_by_id(player_id)
    except HTTPException as e:
        assert e.status_code == 404, "El codigo de estado de la respuesta no es 404(NOT FOUND)"
        assert e.detail == "Player not found", "El detalle de la respuesta no es el esperado."
    else:
        assert False, "No se lanzó la excepción HTTPException."


@db_session
def add_card_to_hand(player_id: int, card_id: int):
    player = Player.get(id=player_id)
    card = Card.get(id=card_id)
    player.hand.add(card)


@db_session
def try_verify_card_in_hand(player_id: int, card_id: int):
    player = Player.get(id=player_id)
    card = Card.get(id=card_id)
    verify_card_in_hand(player, card)


def test_verify_card_in_hand():
    player_id = create_test_player()
    add_card_to_hand(player_id, 1)
    try:
        try_verify_card_in_hand(player_id, 1)
    except HTTPException as e:
        assert False, f"Se lanzó la excepción {e.status_code}. {e.detail}"
    finally:
        client.delete(f'/players/{player_id}')


def test_verify_card_in_hand_fail():
    player_id = create_test_player()
    try:
        try_verify_card_in_hand(player_id, 1)
    except HTTPException as e:
        assert e.status_code == 400, "El codigo de estado de la respuesta no es 400(BAD REQUEST)"
        assert e.detail == "Card not in player hand", "El detalle de la respuesta no es el esperado."
    else:
        assert False, "No se lanzó la excepción HTTPException."
    finally:
        client.delete(f'/players/{player_id}')
