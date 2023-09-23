from fastapi import APIRouter, status, HTTPException
from typing import List
from . import services
from .schemas import *


router = APIRouter(
    prefix="/players",
    tags=["players"],
)


@router.get("/")
async def get_all() -> List[PlayerOut]:
    return services.get_all()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create(new_person: PlayerIn):
    return services.create(new_person)
    