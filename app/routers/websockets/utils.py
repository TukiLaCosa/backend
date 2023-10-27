from fastapi import WebSocket
from pony.orm import db_session, select
from app.database.models import Player, Game
from ..games import services as games_services
from ..games import utils as games_utils
from ..players.utils import find_player_by_id
from ..cards.schemas import CardType
from typing import Dict, List
import random


@db_session
def get_players_id(game_name: str) -> List[Player]:
    gameInformation = games_services.get_game_information(game_name)
    result = []
    if gameInformation:
        for p in gameInformation.list_of_players:
            result.append(p.id)
    return result


@db_session
def flamethrower_cheat(game_name: str, player_id: int):
    game: Game = games_utils.find_game_by_name(game_name)
    player: Player = find_player_by_id(player_id)
    games_utils.verify_player_in_game(player_id, game_name)

    player_hand = list(player.hand)
    elegible_cards = [c for c in player_hand if c.type != CardType.THE_THING]
    if elegible_cards:
        random_card = random.choice(elegible_cards)
        flamethrower_card = select(
            c for c in game.draw_deck if 22 <= c.id and c.id <= 26).first()
        if flamethrower_card:
            game.draw_deck.remove(flamethrower_card)
            game.draw_deck_order.remove(flamethrower_card.id)

        else:
            flamethrower_card = select(
                c for c in game.discard_deck if 22 <= c.id and c.id <= 26).first()
            if flamethrower_card:
                game.discard_deck.remove(flamethrower_card)

        if flamethrower_card and random_card:
            player.hand.remove(random_card)
            player.hand.add(flamethrower_card)


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
                "event": "message",
                "from": message_from,
                "message": message
            }
            await self.active_connections[player_id].send_json(json_msg)
        except KeyError:
            pass

    async def send_event_to(self, player_id: int, message):
        try:
            await self.active_connections[player_id].send_json(message)
        except KeyError:
            pass

    async def send_event_to_all_players_in_game(self, game_name: str, message):
        players_to_send_message = get_players_id(game_name)
        for player_id, websocket in self.active_connections.items():
            if player_id in players_to_send_message:
                await websocket.send_json(message)

    async def send_event_to_other_players_in_game(self, game_name: str, message, excluded_id: int):
        players_to_send_message = get_players_id(game_name)
        for player_id, websocket in self.active_connections.items():
            if player_id in players_to_send_message:
                if player_id != excluded_id:
                    await websocket.send_json(message)

    async def broadcast(self, message):
        for player_id, websocket in self.active_connections.items():
            await websocket.send_json(message)


player_connections = ConnectionManager()
