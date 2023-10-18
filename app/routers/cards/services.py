from pony.orm import *
from app.database.models import Game, Player, Card
from app.routers.games.utils import find_game_by_name
from app.routers.players.services import find_player_by_id
import random
from .schemas import *
from fastapi import HTTPException, status


@db_session
def get_cards() -> list[CardResponse]:
    cards = Card.select()
    cards_list = [CardResponse(
        id=card.id,
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


@db_session
def build_deck(players: int) -> List[Card]:
    deck = list(Card.select(lambda c: c.number <= players and
                            c.name != 'La Cosa'))
    the_thing = Card.get(name='La Cosa')

    if the_thing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The card "The Thing" not found.'
        )

    random.shuffle(deck)

    # Insert the The Thing card making sure that
    # it will go to a player's hand on the first deal.
    random_index = random.randint(0, players - 1)
    deck.insert(random_index, the_thing)

    return deck


@db_session
def deal_cards_to_players(game: Game, deck: List[Card]):
    for _ in range(4):
        for player in game.players:
            card = deck.pop(0)
            player.hand.add(card)


@db_session
def card_is_in_player_hand(card_name: str, player: Player) -> bool:
    card = player.hand.select(lambda c: c.name == card_name).count()
    return card > 0
