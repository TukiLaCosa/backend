from pony.orm import db_session
from fastapi import HTTPException, status
from app.database.models import Card
from ..cards.schemas import CardSubtype, CardActionName


@db_session
def find_card_by_id(card_id: int):
    card = Card.get(id=card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    return card


def verify_action_card(card: Card):
    if card.subtype != CardSubtype.ACTION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card is not an ACTION card"
        )


@db_session
def get_card_name_by_id(card_id: int) -> str:
    card = find_card_by_id(card_id)
    return card.name


@db_session
def get_card_type_by_id(card_id: int) -> str:
    card: Card = find_card_by_id(card_id)
    return card.type


@db_session
def is_flamethrower(card_id: int) -> bool:
    card: Card = find_card_by_id(card_id)
    return (card.name == CardActionName.FLAMETHROWER)

@db_session
def is_whiskey(card_id: int) -> bool:
    card: Card = find_card_by_id(card_id)
    return (card.name == CardActionName.WHISKEY)
