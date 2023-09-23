from fastapi import APIRouter, status, HTTPException
from typing import List
from . import services
from .schemas import *


router = APIRouter(
    prefix="/players",
    tags=["players"],
)


@router.get("/")
def get_all() -> List[PlayerResponse]:
    return services.get_all()


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=PlayerCreationOut)
def create(new_person: PlayerCreationIn):
    return services.create(new_person)
