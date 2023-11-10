from pydantic import BaseModel, ConfigDict, Field, computed_field
from typing import List, Optional
from enum import Enum
from ..cards.schemas import CardResponse


class PlayerRol(str, Enum):
    HUMAN = 'HUMAN'
    THE_THING = 'THE_THING'
    INFECTED = 'INFECTED'
    ELIMINATED = 'ELIMINATED'


class BasePlayer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(min_length=3, max_length=30)


class PlayerCreationIn(BasePlayer):
    pass


class PlayerCreationOut(BasePlayer):
    id: int


class PlayerUpdateIn(BaseModel):
    name: Optional[str] = None


class PlayerResponse(BasePlayer):
    id: int
    position: int
    rol: PlayerRol


class PlayerInfo(PlayerResponse):
    rol: PlayerRol
    hand: List[CardResponse]

    @computed_field
    @property
    def was_the_thing(self) -> bool:
        card_names = map(lambda card: card.name, self.hand)
        return 'La Cosa' in card_names
