from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Optional
from enum import Enum


class CardType(str, Enum):
    PANIC = 'PANIC'
    GET_AWAY = 'GET_AWAY'


class BaseCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    number: int = Field(
        ge=1, le=109)
    type: CardType
    name: str = Field(
        min_length=3, max_length=50)
    description: str = Field(
        min_length=3, max_length=50)


class CardCreationIn(BaseCard):
    pass

    # esto tiene que estar acá o en base?
    # type: CardType
    # name: str = Field(min_length=3, max_length=50)
    # description: str = Field(min_length=3, max_length=50)

#el número podría ser el id
class CardCreationOut(BaseCard):
    id: int


class CardUpdateIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    game_discard_deck_name: Optional[str] = Field(
        None, min_length=3, max_length=50)
    game_draw_deck_name: Optional[str] = Field(
        None, min_length=3, max_length=50)
    players_hand_id: Optional[int]


class CardUpdateOut(BaseCard):
    pass


class CardResponse(BaseCard):
    pass
