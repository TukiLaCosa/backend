from fastapi import WebSocket, WebSocketDisconnect
from .utils import *
import asyncio


async def send_event_cheat_used(player_id: int):
    json_msg = {
        "event": "cheat_used"
    }
    await player_connections.send_event_to(player_id, json_msg)


async def send_list_of_cheats(player_id: int):
    cheat_messages: list[str] = [
        'Soy Loki, Dios de las mentiras, estos son algunos cheats que puedes usar...',
        '[lz | lanzallamas | flamethrower]: Obtienes una carta lanzallamas',
        '[ws | whiskey | whisky]: Obtienes una carta whiskey',
        '[ups | ooops]: Obtienes una carta ups!',
        '[olv | olvidadizo | forgetful]: Obtienes una carta olvidadizo',
        '[uno dos | one two]: Obtienes una carta uno, dos...',
        '[sed | seducción | seduction]: Obtienes una carta de seducción'
    ]
    for message in cheat_messages:
        await player_connections.send_message(player_id, 'Loki', message)
        await asyncio.sleep(0.25)


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

    elif message == 'lz' or message == 'lanzallamas' or message == 'flamethrower':
        apply_cheat(game_name, player_id, range(22, 27))
        await send_event_cheat_used(player_id)

    elif message == 'ws' or message == 'whisky' or message == 'whiskey':
        apply_cheat(game_name, player_id, range(40, 43))
        await send_event_cheat_used(player_id)

    elif message == 'ups' or message == 'ooops':
        apply_cheat(game_name, player_id, range(108, 109))
        await send_event_cheat_used(player_id)

    elif message == 'olv' or message == 'olvidadizo' or message == 'forgetful':
        apply_cheat(game_name, player_id, range(93, 94))
        await send_event_cheat_used(player_id)

    elif message == 'uno dos' or message == 'one two':
        apply_cheat(game_name, player_id, range(94, 96))
        await send_event_cheat_used(player_id)

    elif message == 'sed' or message == 'seducción' or message == 'seduction':
        apply_cheat(game_name, player_id, range(55, 62))
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
