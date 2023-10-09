from typing import List
from fastapi import WebSocket, HTTPException, status
from pony.orm import db_session
from app.database.models import Game


@db_session
def find_game_by_name(game_name: str):
    game = Game.get(name=game_name)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )

    return game


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def diconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message):
        for connection in self.active_connections:
            await connection.send_json(message)


class GameManager:
    def __init__(self):
        self.games = {}

    def new_game(self, game_name: str):
        self.games[game_name] = ConnectionManager()

    def end_game(self, game_name: str):
        self.games.pop(game_name)

    def return_game(self, game_name: str):
        return self.games[game_name]


gameManager = GameManager()
