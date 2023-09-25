from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.config import settings
from app.routers.players import players
from app.routers.games import games

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


@app.get("/")
async def root():
    return {"message": "Hello World"}
