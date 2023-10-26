from pony.orm import db_session, select
from app.database.models import Game, Player
from fastapi import WebSocket, WebSocketDisconnect
from .utils import player_connections, get_players_id
from ..cards.schemas import CardType
import random


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
                
                if message == 'lz':
                    with db_session:
                        player: Player = select(p for p in Player if p.name == message_from).first()
                        game: Game = select(g for g in Game if g.name == data["game_name"]).first()
                        player_hand_list = list(player.hand)
                        elegible_cards = [
                            c for c in player_hand_list if c.type != CardType.THE_THING]
                        random_card = random.choice(elegible_cards)
                        flamethrower_card = select(c for c in game.discard_deck if 22 <= c.id and c.id <= 26).first()
                        if flamethrower_card:
                            player.hand.remove(random_card)
                            player.hand.add(flamethrower_card)
                            game.discard_deck.add(random_card)
                            game.discard_deck.remove(flamethrower_card)
                    json_msg = {
                        "event": "cheat_flamethrower"
                    }
                    await player_connections.send_event_to(player.id, json_msg)
    except WebSocketDisconnect:
        player_connections.disconnect(player_id)
