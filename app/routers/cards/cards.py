from fastapi import APIRouter, status, HTTPException
from typing import List
from . import services
from .schemas import *


router = APIRouter(
    prefix="/cards",  # prefix="/games/{name}/cards" ????
    tags=["cards"],
)


# No me queda claro que endpoints asignar a cada uno.

# get all, get by deck, get by player, get by game, get by id ?
# Rta >> Este get es para listar todas las cartas
@router.get("/", response_model=list[CardResponse], status_code=status.HTTP_200_OK)
def get_cards():
    return services.get_cards()

# Se deberian poder crear cartas con igual número?
# Rta >> Si porque los numeros indican para la cantidad de jugadores que se deben usar
# Vale la pena tener un campo id ya que tenemos el de número?
# Rta >> Si porque como dije antes, los numeros se repiten y el ID tiene que ser unico


@router.post("/", response_model=CardCreationOut, status_code=status.HTTP_201_CREATED)
def create_card(card_data: CardCreationIn):
    return services.create_card(card_data)


@router.patch("/{card_id}", response_model=CardUpdateOut, status_code=status.HTTP_200_OK)
def update_card(card_id: int, card_data: CardUpdateIn):
    return services.update_card(card_id, card_data)


@router.delete("/{card_id}", response_model=None, status_code=status.HTTP_200_OK)
def delete_card(card_id: int):
    return services.delete_card(card_id)


# Está bien separar los dos casos?
# El primero agrega un game a cualquier set
# y el segundo elmina uno de cualquiera
# De todas formas no me está andando esto no se bien por que je

# @router.patch("/", response_model=CardUpdateOut, status_code=status.HTTP_200_OK)
# def update_card_remove(card_id: int, new_data: CardUpdateIn):
#     return services.update_card_remove(card_id, new_data)