from fastapi import WebSocket, WebSocketDisconnect
from .utils import player_connections


async def websocket_games(player_id: int, websocket: WebSocket):
    await player_connections.connect(player_id, websocket)

    try:
        while True:
            data = await websocket.receive()
            '''
            Aca si recibimo data.event == message entonces mandamos el mensaje
            al resto de los jugadores por ejemplo.
            O si es un data.event == disconnect entonces debemos sacar el websocket
            de la lista de player_connections.
            '''
    except WebSocketDisconnect:
        player_connections.disconnect(player_id)
