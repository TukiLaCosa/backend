from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Optional
from enum import Enum


class CardType(str, Enum):
    PANIC = 'PANIC'
    GET_AWAY = 'GET_AWAY'


class BaseCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    number: int = Field(
        ge=4, le=12)
    type: CardType
    name: str = Field(
        min_length=3, max_length=50)
    description: str = Field(
        min_length=3, max_length=250)


class CardCreationIn(BaseCard):
    pass


class CardCreationOut(BaseCard):
    pass


class CardUpdateIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    number: Optional[int] = Field(
        None, ge=4, le=12, description="Optional number of the card."
    )
    type: Optional[CardType] = Field(
        None, description="Optional card type."
    )
    name: Optional[str] = Field(
        None, min_length=3, max_length=50, desctiption="Optional name of the card."
    )
    description: Optional[str] = Field(
        None, min_length=3, max_length=250, description="Optional description of the card."
    )


class CardUpdateOut(BaseCard):
    pass


class CardResponse(BaseCard):
    pass
