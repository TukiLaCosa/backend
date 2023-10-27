from fastapi import WebSocket, WebSocketDisconnect
from .utils import *


async def send_event_cheat_used(player_id: int):
    json_msg = {
        "event": "cheat_used"
    }
    await player_connections.send_event_to(player_id, json_msg)


async def send_list_of_cheats(player_id: int):
    cheats: list[str] = []
    cheats.append(
        'lz or lanzallamas or flamethrower: Obtienes una carta lanzallamas')
    cheats.append('ws or whiskey or whisky: Obtienes una carta whiskey')
    for c in cheats:
        await player_connections.send_message(player_id, 'Loki', c)


async def handle_message(data, player_id):
    message_from = data["from"]
    message = data["message"]
    game_name = data["game_name"]
    players = get_players_id(game_name)

    for i in players:
        if i != player_id:
            await player_connections.send_message(player_id=i, message_from=message_from, message=message)
    if message == 'cheats':
        await send_list_of_cheats(player_id)
    if message == 'lz' or message == 'lanzallamas' or message == 'flamethrower':
        flamethrower_cheat(game_name, player_id)
        await send_event_cheat_used(player_id)
    if message == 'ws' or message == 'whisky' or message == 'whiskey':
        whiskey_cheat(game_name, player_id)
        await send_event_cheat_used(player_id)


async def websocket_games(player_id: int, websocket: WebSocket):
    await player_connections.connect(player_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            if (data["event"] == "message"):
                await handle_message(data, player_id)
    except WebSocketDisconnect:
        player_connections.disconnect(player_id)
