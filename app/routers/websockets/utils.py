from fastapi import WebSocket
from typing import Dict


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, player_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[player_id] = websocket

    def disconnect(self, player_id: int):
        del self.active_connections[player_id]

    async def send_message(self, player_id: int, message):
        await self.active_connections[player_id].send_json(message)

    async def broadcast(self, message):
        for player_id, websocket in self.active_connections.items():
            await websocket.send_json(message)


player_connections = ConnectionManager()
