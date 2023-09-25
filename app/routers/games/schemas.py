from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Optional
from enum import Enum


class GameStatus(str, Enum):
    UNSTARTED = 'UNSTARTED'
    STARTED = 'STARTED'
    ENDED = 'ENDED'


class BaseGame(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(min_length=3, max_length=30,
                      description="The name of the game")
    min_players: int = Field(
        ge=4, le=12, description="The minimum number of players allowed.")
    max_players: int = Field(
        ge=4, le=12, description="The maximum number of players allowed.")

    @model_validator(mode='after')
    def check_min_lte_max(self) -> 'BaseGame':
        if self.max_players < self.min_players:
            raise ValueError('max_players can not be less than min_players')
        return self


class GameCreationIn(BaseGame):
    password: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Optional password to join the game.")
    host_player_id: int


class GameCreationOut(BaseGame):
    status: GameStatus
    host_player_id: int
    is_private: bool


class GameUpdateIn(BaseGame):
    password: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Optional password to join the game.")


class GameResponse(BaseGame):
    host_player_id: int
    status: GameStatus
    is_private: bool
    players_joined: int
