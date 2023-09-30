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


'''
@db_session
def find_card_by_id(id: int) -> Card:
    card = Card.get(id=id)

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with id '{id}' not found."
        )

    return card
'''


@db_session
def update_card(card_id: int, request_data: CardUpdateIn) -> CardUpdateOut:
    card = Card.get(id=card_id)

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
        )
    if card_id != card.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid card id"
        )

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
    card = Card.get(id=card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
        )
    if card_id != card.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid card id"
        )
    card.delete()
    return {"message": "Card deleted"}


'''
@db_session
def update_card_add(id: int, update_data: CardUpdateIn) -> Card:
    card = find_card_by_id(id)

    if not update_data.game_draw_deck_name:
        game = find_game_by_name(update_data.game_draw_deck_name)
        if game in card.games_draw_deck:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # ?? no se que código usar
            detail=f"the card has already been added to the deck."
        )
        card.games_draw_deck.add(game)

    if not update_data.game_discard_deck_name:
        game = find_game_by_name(update_data.game_discard_deck_name)
        if game in card.games_discard_deck:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # ?? no se que código usar
            detail=f"the card has already been added to the deck."
        )
        card.games_discard_deck.add(game)

    if not update_data.players_hand_id:
        player = find_player_by_id(update_data.players_hand_id)
        card.players_hand.add(player)

    return card



@db_session
def update_card_remove(id: int, update_data: CardUpdateIn) -> Card:
    card = find_card_by_id(id)

    if not update_data.game_draw_deck_name:
        game = find_game_by_name(update_data.game_draw_deck_name)
        if game not in card.games_draw_deck:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # ?? no se que código usar
            detail=f"the card has already been removed from the deck."
        )
        card.games_draw_deck.remove(game)

    if not update_data.game_discard_deck_name:
        game = find_game_by_name(update_data.game_discard_deck_name)
        if game not in card.games_discard_deck:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # ?? no se que código usar
            detail=f"the card has already been removed from the deck."
        )
        card.games_discard_deck.remove(game)

    if not update_data.players_hand_id:
        player = find_player_by_id(update_data.players_hand_id)
        card.players_hand.remove(player)

    return card'''
