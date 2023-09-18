from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from typing import List, Optional
from enum import Enum


class PlayerRol(str, Enum):
    HUMAN = 'HUMAN'
    THE_THING = 'THE_THING'
    INFECTED = 'INFECTED'
    ELIMINATED = 'ELIMINATED'


class BasePlayer(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel)

    name: str = Field(min_length=3, max_length=30)


class PlayerIn(BasePlayer):
    pass


class PlayerOut(BasePlayer):
    id: int
    rol: Optional[PlayerRol] = None
