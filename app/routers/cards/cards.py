from fastapi import APIRouter, status, HTTPException
from typing import List
from . import services
from .schemas import *


router = APIRouter(
    prefix="/cards", #prefix="/games/cards" ????
    tags=["cards"],
)

@router.get() #get mazo #

@router.post() #

@router.delete() #jugar carta?

@router.put() #jugar carta