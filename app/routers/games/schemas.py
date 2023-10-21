from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Optional
from enum import Enum
from ..players.schemas import PlayerResponse, PlayerInfo
from ..cards.schemas import CardType, CardResponse


class GameStatus(str, Enum):
    UNSTARTED = 'UNSTARTED'
    STARTED = 'STARTED'
    ENDED = 'ENDED'


class RoundDirection(str, Enum):
    CLOCKWISE = 'CLOCKWISE'
    COUNTERCLOCKWISE = 'COUNTERCLOCKWISE'


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


class GameUpdateIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    min_players: int = Field(
        ge=4, le=12, description="The minimum number of players allowed.")
    max_players: int = Field(
        ge=4, le=12, description="The maximum number of players allowed.")
    password: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Optional password to join the game.")

    @model_validator(mode='after')
    def check_min_lte_max(self) -> 'BaseModel':
        if self.max_players < self.min_players:
            raise ValueError('max_players can not be less than min_players')
        return self


class GameUpdateOut(BaseGame):
    is_private: bool
    status: GameStatus


class GameResponse(BaseGame):
    host_player_id: int
    status: GameStatus
    is_private: bool
    num_of_players: int


class GameInformationIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    player_id: int
    password: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Optional password to join the game.")


class GameInformationOut(GameUpdateOut):
    host_player_name: str
    host_player_id: int
    num_of_players: int
    list_of_players: List[PlayerResponse]


class GameStartOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    list_of_players: List[PlayerResponse]
    status: GameStatus
    top_card_face: CardType


class DiscardInformationIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    player_id: int
    card_id: int


class PlayInformation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    card_id: int
    player_id: int
    objective_player_id: Optional[int] = Field(
        None, description="Optional objective player."
    )
    card_to_exchange: Optional[int] = Field(
        None, description="Optional card to exchange."
    )


class DrawInformationIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    player_id: int


class DrawInformationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    player_id: int
    card: CardResponse
    top_card_face: CardType


class GameResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reason: str
    winners: List[PlayerInfo]
    losers: List[PlayerInfo]

class IntentionExchangeInformationIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    player_id: int # ID jugador que inicia la intencion
    card_id: int # Card ID del jugador que inicia la intencion

class InterchangeInformationIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    player_id: int # ID jugador que recibe la intencion
    card_id: int # Card ID del jugador que recibe la intencion
    objective_player_id: int # ID jugador que inicia la intencion
    objective_card_id: int # Card ID del jugador que inicia la intencion

