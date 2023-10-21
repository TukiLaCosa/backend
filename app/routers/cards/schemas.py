from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Optional
from enum import Enum


class CardType(str, Enum):
    PANIC = 'PANIC'
    STAY_AWAY = 'STAY_AWAY'
    THE_THING = 'THE_THING'


class CardSubtype(str, Enum):
    CONTAGION = 'CONTAGION'
    ACTION = 'ACTION'
    DEFENSE = 'DEFENSE'
    OBSTACLE = 'OBSTACLE'
    PANIC = 'PANIC'


class CardActionName(str, Enum):
    FLAMETHROWER = 'Lanzallamas'
    ANALYSIS = 'Análisis'
    AXE = 'Hacha'
    SUSPICIOUS = 'Sospecha'
    WHISKEY = 'Whisky'
    RESOLUTE = 'Determinación'
    WATCH_YOUR_BACK = 'Vigila tus espaldas'
    CHANGE_PLACES = '¡Cambio de lugar!'
    BETTER_RUN = '¡Más vale que corras!'
    SEDUCTION = 'Seducción'


class BaseCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    number: int = Field(
        ge=4, le=12)
    type: CardType
    subtype: CardSubtype
    name: str = Field(
        min_length=3, max_length=50)
    description: str = Field(
        min_length=3, max_length=1000)


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
    subtype: Optional[CardSubtype] = Field(
        None, description="Optional card subtype."
    )
    name: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Optional name of the card."
    )
    description: Optional[str] = Field(
        None, min_length=3, max_length=1000
    )


class CardUpdateOut(BaseCard):
    pass


class CardResponse(BaseCard):
    id: int = Field(
        ge=1, le=108
    )
