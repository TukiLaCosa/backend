from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.config import settings
from app.routers.players import players
from app.routers.games import games
from app.routers.cards import cards
from app.routers.websockets import websockets
from .utils import show_initial_image
import threading

app = FastAPI()

# Allowing requests from other origins (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mapping api routers
app.include_router(players.router)
app.include_router(games.router)
app.include_router(cards.router)
app.include_router(websockets.router)

# This displays the initial image with the sound
t = threading.Thread(target=show_initial_image)
t.start()
