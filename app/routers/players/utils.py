from pony.orm import db_session
from fastapi import HTTPException, status
from app.database.models import Player, Card


@db_session
def find_player_by_id(player_id: int):
    player = Player.get(id=player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    return player


@db_session
def verify_card_in_hand(player: Player, card: Card):
    if card in player.hand:
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card not in player hand"
        )
