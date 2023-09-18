from fastapi import APIRouter, status, HTTPException
from typing import List
from . import services
from .schemas import *


router = APIRouter(
    prefix="/players",
    tags=["players"],
)


@router.get("/")
def get_all() -> List[PlayerOut]:
    return services.get_all()


@router.post('/', status_code=status.HTTP_201_CREATED)
def create(new_person: PlayerIn) -> PlayerOut:
    return services.create(new_person)
