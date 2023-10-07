from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Game, Player
from app.routers.games.schemas import GameCreationOut
from pony.orm import db_session

client = TestClient(app)


@db_session
def create_test_player(name: str):
    return Player(name=name)


@db_session
def cleanup_database():
    Game.select().delete()
    Player.select().delete()


def test_create_successfull_game():
    cleanup_database()
    test_player = create_test_player("Ignacio")

    game_data = {
        "name": "TestGame",
        "min_players": 4,
        "max_players": 6,
        "password": "secret",
        "host_player_id": test_player.id
    }

    response = client.post("/games", json=game_data)

    assert response.status_code == 201, "El codigo de estado de la respuesta no es 201(Created)"

    with db_session:
        created_game = Game.get(name=game_data["name"])
    assert created_game is not None

    game_creation_response = GameCreationOut(**response.json())
    assert game_creation_response.name == game_data[
        "name"], "El nombre del juego en la respuesta no coincide con el nombre proporcionado."
    assert game_creation_response.status == "UNSTARTED", "El estado del juego en la respuesta no es 'UNSTARTED'."
    assert game_creation_response.min_players == game_data[
        "min_players"], "El número mínimo de jugadores en la respuesta no coincide con el valor proporcionado."
    assert game_creation_response.max_players == game_data[
        "max_players"], "El número máximo de jugadores en la respuesta no coincide con el valor proporcionado."
    assert game_creation_response.is_private == True, "El juego no se creó como privado en la respuesta."
    assert game_creation_response.host_player_id == test_player.id, "El ID del jugador anfitrión en la respuesta no coincide con el ID del jugador de prueba."
    cleanup_database()


def test_create_without_player_in_ddbb():
    cleanup_database()
    game_data = {
        "name": "TestGame",
        "min_players": 4,
        "max_players": 6,
        "password": "secret",
        "host_player_id": 1
    }
    response = client.post("/games", json=game_data)
    assert response.status_code == 404, "Se esperaba un código de estado 404 (Not Found) ya que el jugador no existe en la base de datos."
    cleanup_database()


def test_create_game_with_a_host_already_hosting():
    cleanup_database()
    test_player = create_test_player("Ignacio")
    game_data = {
        "name": "TestGame",
        "min_players": 4,
        "max_players": 6,
        "password": "secret",
        "host_player_id": test_player.id
    }
    for i in range(2):
        response = client.post("/games", json=game_data)
    assert response.status_code == 400, "Se esperaba un código de estado 400 (Bad Request) ya que el jugador ya está hospedando un juego."
    cleanup_database()


def test_create_game_with_same_name():
    cleanup_database()
    test_player1 = create_test_player("Ignacio")
    test_player2 = create_test_player("Ezequiel")
    game_data = [
        {
            "name": "TestGame",
            "min_players": 4,
            "max_players": 6,
            "password": "secret",
            "host_player_id": test_player1.id
        }, {
            "name": "TestGame",
            "min_players": 4,
            "max_players": 6,
            "password": "secret",
            "host_player_id": test_player2.id
        }
    ]
    for i in game_data:
        response = client.post("/games", json=i)
    assert response.status_code == 400, "Se esperaba un código de estado 400 (Bad Request) ya que un juego con el mismo nombre ya existe."
    cleanup_database()
