from fastapi import WebSocket, WebSocketDisconnect
from .utils import player_connections, get_players_id, flamethrower_cheat


async def handle_message(data, player_id):
    message_from = data["from"]
    message = data["message"]
    game_name = data["game_name"]
    players = get_players_id(game_name)

    for i in players:
        if i != player_id:
            await player_connections.send_message(player_id=i, message_from=message_from, message=message)

    if message == 'lz':
        flamethrower_cheat(game_name, player_id)
        json_msg = {
            "event": "cheat_flamethrower"
        }
        await player_connections.send_event_to(player_id, json_msg)


async def websocket_games(player_id: int, websocket: WebSocket):
    await player_connections.connect(player_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            if (data["event"] == "message"):
                await handle_message(data, player_id)
    except WebSocketDisconnect:
        player_connections.disconnect(player_id)
