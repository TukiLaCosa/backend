from fastapi import APIRouter, WebSocket
from . import services

router = APIRouter(
    prefix="/ws",
    tags=["ws"],
)


@router.websocket("/{player_id}")
def websockets_games(player_id: int, websocket: WebSocket):
    return services.websocket_games(player_id, websocket)
