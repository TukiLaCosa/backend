from fastapi import WebSocket
from typing import List


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                self.active_connections.remove(connection)


class GameManager:
    def __init__(self):
        self.games_connections = {}

    def new_game(self, game_name: str):
        self.games_connections[game_name] = ConnectionManager()

    def end_game(self, game_name: str):
        del self.games_connections[game_name]

    def return_game_connection(self, game_name: str):
        return self.games_connections[game_name]


player_connections = ConnectionManager()
# gamesManager = GameManager()
