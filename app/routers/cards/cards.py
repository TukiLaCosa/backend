from fastapi import APIRouter, status, HTTPException
from typing import List
from . import services
from .schemas import *


router = APIRouter(
    prefix="/cards",
    tags=["cards"],
)


@router.get("/", response_model=list[CardResponse], status_code=status.HTTP_200_OK)
def get_cards():
    return services.get_cards()


@router.post("/", response_model=CardCreationOut, status_code=status.HTTP_201_CREATED)
def create_card(card_data: CardCreationIn):
    return services.create_card(card_data)


@router.patch("/{card_id}", response_model=CardUpdateOut, status_code=status.HTTP_200_OK)
def update_card(card_id: int, card_data: CardUpdateIn):
    return services.update_card(card_id, card_data)


@router.delete("/{card_id}", status_code=status.HTTP_200_OK)
def delete_card(card_id: int):
    return services.delete_card(card_id)

