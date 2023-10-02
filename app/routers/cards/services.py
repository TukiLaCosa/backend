from pony.orm import *
from app.database.models import Game, Player, Card
from app.routers.games.services import find_game_by_name
from app.routers.players.services import find_player_by_id
from .schemas import *
from fastapi import HTTPException, status


@db_session
def get_cards() -> list[CardResponse]:
    cards = Card.select()
    cards_list = [CardResponse(
        number=card.number,
        type=card.type,
        name=card.name,
        description=card.description
    ) for card in cards]
    return cards_list


@db_session
def create_card(card_data: CardCreationIn) -> Card:
    new_card = Card(
        number=card_data.number,
        type=card_data.type,
        name=card_data.name,
        description=card_data.description
    )

    return new_card


@db_session
def find_card_by_id(id: int) -> Card:
    card = Card.get(id=id)

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with id '{id}' not found."
        )
    if id != card.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid card id"
        )

    return card


@db_session
def update_card(card_id: int, request_data: CardUpdateIn) -> CardUpdateOut:
    card = find_card_by_id(card_id)

    card.number = request_data.number
    card.type = request_data.type
    card.name = request_data.name
    card.description = request_data.description
    return CardUpdateOut(
        number=card.number,
        type=card.type,
        name=card.name,
        description=card.description
    )


@db_session
def delete_card(card_id: int):
    card = find_card_by_id(card_id)
    card.delete()
    return {"message": "Card deleted"}
