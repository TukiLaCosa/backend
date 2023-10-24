from pony.orm import db_session
from fastapi import HTTPException, status
from app.database.models import Card
from ..cards.schemas import CardType, CardSubtype


@db_session
def find_card_by_id(card_id: int) -> Card:
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


def verify_panic_card(card: Card):
    if card.type != CardType.PANIC:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card is not a PANIC card"
        )


@db_session
def get_card_name_by_id(card_id: int) -> str:
    card = find_card_by_id(card_id)
    return card.name


@db_session
def get_card_type_by_id(card_id: int) -> str:
    card: Card = find_card_by_id(card_id)
    return card.type
