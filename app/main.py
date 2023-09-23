from fastapi import FastAPI
from app.routers.players import players
from app.routers.games import games

app = FastAPI()

# Mapping api routers
app.include_router(players.router)
app.include_router(games.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
