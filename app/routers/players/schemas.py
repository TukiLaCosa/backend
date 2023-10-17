from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from enum import Enum


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
