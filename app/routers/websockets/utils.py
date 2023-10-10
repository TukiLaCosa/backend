from fastapi import WebSocket
from pony.orm import db_session
from app.database.models import Player
from ..games import services as games_services
from typing import Dict, List
import json


@db_session
def get_players_id(game_name: str) -> List[Player]:
    gameInformation = games_services.get_game_information(game_name)
    result = []
    if gameInformation:
        for p in gameInformation.list_of_players:
            result.append(p.id)
    return result


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, player_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[player_id] = websocket

    def disconnect(self, player_id: int):
        del self.active_connections[player_id]

    async def send_message(self, player_id: int, message_from: str, message: str):
        try:
            json_msg = {
                "from": message_from,
                "message": message
            }
            await self.active_connections[player_id].send_json(json_msg)
        except KeyError:
            pass

    async def broadcast(self, message):
        for player_id, websocket in self.active_connections.items():
            await websocket.send_json(message)


player_connections = ConnectionManager()
