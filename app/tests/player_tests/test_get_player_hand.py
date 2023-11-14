from fastapi.testclient import TestClient
from pony.orm import db_session
from app.database.models import Card, Player
from app.main import app


client = TestClient(app)


@db_session
def create_test_hand(player_id: int) -> list:
    player = Player.get(id=player_id)
    result = []
    for i in range(1, 5):
        card = Card.get(id=i)
        player.hand.add(card)
        result.append(card.id)
    return result


def test_get_player_hand_succes():
    test_hand = create_test_hand(1)

    response = client.get(
        f'/players/1/hand')
    assert response.status_code == 200, "El codigo de estado de la respuesta no es 200(OK)"

    assert len(
        response.json()) == len(test_hand), "El número de cartas en la mano del jugador no es el esperado."

    # Verifico que no haya cartas duplicadas en la mano del jugador
    card_ids_in_hand = [card['id'] for card in response.json()]
    assert len(card_ids_in_hand) == len(set(card_ids_in_hand)
                                        ), "Se encontraron cartas duplicadas en la mano del jugador."

    for i in range(len(response.json())):
        assert response.json()[
            i]['id'] in test_hand, f"Las cartas en la mano del jugador no son las esperadas. No se encontró la carta con ID {response.json()[i]['id']} en la mano del jugador."
