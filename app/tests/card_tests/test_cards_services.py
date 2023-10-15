from fastapi.testclient import TestClient
from app.main import app
from app.database.models import *
from app.routers.cards.schemas import *
from fastapi import status
from pony.orm import db_session
from app.database.initialize_data import populate_card_table
from app.routers.cards.services import *

client = TestClient(app)


@db_session
def create_card_for_testing(id: int) -> Card:
    return Card(id=id, number=4, type="THE_THING", name="The Thing",
                description="You are the thing, infect or kill everyone")


@db_session
def create_test_player(name: str):
    return Player(name=name)


@db_session
def create_test_game(name, min_players, max_players, password, host_player_id):
    host = Player.get(id=host_player_id)
    game = Game(
        name=name,
        min_players=min_players,
        max_players=max_players,
        password=password,
        host=host
    )
    commit()
    return game


@db_session
def cleanup_database() -> None:
    Card.select().delete()
    Game.select().delete()
    Player.select().delete()


# Test cases
@db_session
def test_build_deal_deck_without_the_thing_4_players() -> None:
    cleanup_database()
    populate_card_table()
    Card.get(type="THE_THING").delete()
    try:
        build_deal_deck(4)
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND
        assert e.detail == "The card \"The Thing\" not found."

    cleanup_database()


def test_build_deal_deck_with_the_thing_on_the_first_hand_4_players() -> None:
    cleanup_database()
    populate_card_table()
    list = build_deal_deck(4)

    for i in range(0, 3):
        result = list[i].name == "The Thing"

    assert result == False
    cleanup_database()


# Este está raro, renegué un toque y quedó muy hardcodeado
@db_session
def test_deal_cards_to_players_4_players() -> None:
    cleanup_database()
    populate_card_table()
    players = []
    names = ["Ignacio", "Anelio", "Ezequiel",
             "Amparo"]
    for name in names:
        players.append(create_test_player(name=name))
        commit()

    game = create_test_game(name="TestGame", min_players=4, max_players=7,
                            password="secret", host_player_id=players[0].id)

    for player in players[0:]:
        game.players.add(player)

    deal_deck = build_deal_deck(4)
    deal_cards_to_players(game, deal_deck)

    for player in players:
        assert len(
            player.hand) == 4, f"El tamaño de la mano del jugador {player.name} esperado es 4. El tamaño de la mano del jugador {player.name} obtenido es {len(player.hand)}."

    cleanup_database()


# lo mismo que el anterior.
@db_session
def test_build_draw_deck_4_players() -> None:
    cleanup_database()

    players = []
    names = ["Ignacio", "Anelio", "Ezequiel",
             "Amparo"]
    for name in names:
        players.append(create_test_player(name=name))
        commit()

    game = create_test_game(name="TestGame", min_players=4, max_players=7,
                            password="secret", host_player_id=players[0].id)

    for player in players[0:]:
        game.players.add(player)

    populate_card_table()
    deal_deck = build_deal_deck(4)
    deal_cards_to_players(game, deal_deck)
    draw_deck = build_draw_deck(deal_deck, 4)

    assert len(
        draw_deck) == 19, f"El tamaño del mazo de robo esperado es 19. El tamaño del mazo de robo obtenido es {len(draw_deck)}."

    cleanup_database()
