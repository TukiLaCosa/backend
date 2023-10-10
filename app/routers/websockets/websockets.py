from fastapi import APIRouter, WebSocket
from . import services

router = APIRouter(
    prefix="/ws",
    tags=["ws"],
)

@router.websocket("/games")
def websockets_games(websocket: WebSocket):
    return services.websocket_games(websocket)