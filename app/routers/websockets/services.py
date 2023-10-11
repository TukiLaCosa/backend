from pony.orm import db_session
from app.database.models import Game, Player
from fastapi import WebSocket, WebSocketDisconnect
from .utils import player_connections, get_players_id


async def websocket_games(player_id: int, websocket: WebSocket):
    await player_connections.connect(player_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            if (data["event"] == "message"):
                message_from = data["from"]
                message = data["message"]
                players = get_players_id(data["game_name"])
                for i in players:
                    if i != player_id:
                        await player_connections.send_message(player_id=i, message_from=message_from, message=message)
    except WebSocketDisconnect:
        player_connections.disconnect(player_id)
