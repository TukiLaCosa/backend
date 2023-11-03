from app.routers.players.schemas import PlayerInfo
from app.routers.cards.schemas import CardResponse
from typing import List


def test_PlayerInfo_schema_was_the_thing_true_success():
    the_thing = CardResponse(id=1, number=4, type="THE_THING", subtype="CONTAGION", name="La Cosa",
                             description="You are La Cosa, infect or kill everyone")

    cards = [
        CardResponse(id=5, number=4, type="PANIC", subtype="PANIC", name="Not La Cosa",
                     description="You are La Cosa, infect or kill everyone"),
        CardResponse(id=5, number=4, type="PANIC", subtype="PANIC", name="Not La Cosa",
                     description="You are La Cosa, infect or kill everyone"),
        the_thing,
        CardResponse(id=5, number=4, type="PANIC", subtype="PANIC", name="Not La Cosa",
                     description="You are La Cosa, infect or kill everyone"),
    ]
    player = PlayerInfo(name="player", id=1, position=1,
                        rol="THE_THING", hand=cards)
    assert player.was_the_thing == True, "El jugador debería tener la carta 'La Cosa' en su mano."


def test_PlayerInfo_schema_was_the_thing_false_success():
    cards = [
        CardResponse(id=5, number=4, type="PANIC", subtype="PANIC", name="Not La Cosa",
                     description="You are La Cosa, infect or kill everyone"),
        CardResponse(id=5, number=4, type="PANIC", subtype="PANIC", name="Not La Cosa",
                     description="You are La Cosa, infect or kill everyone"),
        CardResponse(id=5, number=4, type="PANIC", subtype="PANIC", name="Not La Cosa",
                     description="You are La Cosa, infect or kill everyone"),
    ]
    player = PlayerInfo(name="player", id=1, position=1,
                        rol="THE_THING", hand=cards)
    assert player.was_the_thing == False, "El jugador no debería tener la carta 'La Cosa' en su mano."
