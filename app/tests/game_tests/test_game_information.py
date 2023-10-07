from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Game, Player
from app.routers.games.schemas import GameInformationOut
from pony.orm import db_session

client = TestClient(app)


@db_session
def create_test_player(name: str):
    return Player(name=name)


@db_session
def create_test_game(name, min_players, max_players, password, host_player_id):
    game_data = {
        "name": name,
        "min_players": min_players,
        "max_players": max_players,
        "password": password,
        "host_player_id": host_player_id
    }
    client.post("/games", json=game_data)


@db_session
def cleanup_database():
    Game.select().delete()
    Player.select().delete()


def test_information_of_created_game():
    cleanup_database()
    test_player = create_test_player("Ignacio")
    create_test_game(name="TestGame", min_players=4, max_players=6,
                     password="secret", host_player_id=test_player.id)
    response = client.get("/games/TestGame")
    assert response.status_code == 200
    game_information_response = GameInformationOut(**response.json())
    assert game_information_response.name == "TestGame", "El nombre del juego no coincide con el esperado."
    assert game_information_response.status == "UNSTARTED", "El estado del juego no coincide con el esperado."
    assert game_information_response.min_players == 4, "El número mínimo de jugadores no coincide con el esperado."
    assert game_information_response.max_players == 6, "El número máximo de jugadores no coincide con el esperado."
    assert game_information_response.is_private == True, "El juego no se marcó como privado en la respuesta."
    assert game_information_response.host_player_id == test_player.id, "El ID del jugador anfitrión no coincide con el esperado."
    assert game_information_response.host_player_name == test_player.name, "El nombre del jugador anfitrión no coincide con el esperado."
    assert game_information_response.num_of_players == 1, "El número de jugadores no coincide con el esperado."
    cleanup_database()


def test_information_of_game_not_found():
    cleanup_database()
    response = client.get("/games/InexistentGame")
    assert response.status_code == 404, "El código de estado de la respuesta no es 404 (Not Found)."
    cleanup_database()
