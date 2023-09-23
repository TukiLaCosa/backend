from pony.orm import PrimaryKey, Required, Set, Optional
from app.database import db


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    game = Optional('Game', reverse='players')
    game_hosting = Optional('Game', reverse='host')
    name = Required(str)
    rol = Optional(str, nullable=True)
    position = Required(int, default="-1")
    hand = Set('Card')


class Game(db.Entity):
    name = PrimaryKey(str, auto=True)
    players = Set(Player, reverse='game')
    host = Required(Player, reverse='game_hosting')
    min_players = Required(int)
    max_players = Required(int)
    password = Optional(str, nullable=True)
    turn = Required(int, default="-1")
    status = Required(str, default='UNSTARTED')
    discard_deck = Set('Card', reverse='games_discard_deck')
    draw_deck = Set('Card', reverse='games_draw_deck')
    round_direction = Required(str, default='clockwise')


class Card(db.Entity):
    id = PrimaryKey(int, auto=True)
    number = Required(int)
    type = Required(str)
    name = Required(str)
    description = Required(str)
    games_discard_deck = Set(Game, reverse='discard_deck')
    games_draw_deck = Set(Game, reverse='draw_deck')
    players_hand = Set(Player)
