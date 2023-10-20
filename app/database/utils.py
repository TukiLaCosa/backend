from pony.orm import db_session, commit
from .models import Player, Game


@db_session
def create_seed_data():
    players = []
    for i in range(1, 7):
        player = Player(name=f"Player{i}")
        players.append(player)
    commit()

    game = Game(name="TestGame",
                min_players=4,
                max_players=12,
                password='secure',
                host=players[0],
                )
    commit()
    players[0].game = game.name
    commit()
    for i in range(1, 6):
        game.players.add(players[i])
