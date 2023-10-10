from fastapi import WebSocket, WebSocketDisconnect
from .utils import player_connections


async def websocket_games(websocket: WebSocket):
    await player_connections.connect(websocket)

    try:
        while True:
            data = await websocket.receive()

    except WebSocketDisconnect:
        player_connections.disconnect(websocket)
