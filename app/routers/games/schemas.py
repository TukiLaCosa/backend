from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Optional
from enum import Enum
# from ..players.schemas import Player


class GameStatus(str, Enum):
    UNSTARTED = 'UNSTARTED'
    STARTED = 'STARTED'
    ENDED = 'ENDED'


class BaseGame(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(min_length=3, max_length=30,
                      description="The name of the game")
    # greather or equal than=4 , less or equal than=12
    min_players: int = Field(
        ge=4, le=12, description="The minimum number of players allowed.")
    # Field() sirve para configurar parámetros del campo
    max_players: int = Field(
        ge=4, le=12, description="The maximum number of players allowed.")
    
    @model_validator(mode='after')
    def check_min_lte_max(self) -> 'BaseGame':
        if self.max_players < self.min_players:
            raise ValueError('max_players can not be less than min_players')
        return self

    # players_count: int
    # status: GameStatus


class GameCreationIn(BaseGame):
    password: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Optional password to join the game.")
    host_player_id: int

    

class GameCreationOut(BaseGame):
    status: GameStatus
    host_player_id: int
    is_private: bool

    # players_count: int (cantidad de jugadores)
    # current_player: List[Player]
