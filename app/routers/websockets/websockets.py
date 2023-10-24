from fastapi import APIRouter, WebSocket
from .utils import player_connections
from . import services

router = APIRouter(
    prefix="/ws",
    tags=["ws"],
)


@router.websocket("/{player_id}")
def websockets_games(player_id: int, websocket: WebSocket):
    return services.websocket_games(player_id, websocket)


@router.get('/{game_name}/send-self-event')
async def send_self_event(game_name: str, event: str):
    await player_connections.send_event_to_all_players_in_game(game_name, {'event': event})
