from fastapi import FastAPI
from app.routers.players import players

app = FastAPI()

# Mapping api routers
app.include_router(players.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
