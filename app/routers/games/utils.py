import random
from typing import List
from fastapi import WebSocket, HTTPException, status
from app.database.models import Game, Player, Card
from pony.orm import *
from .schemas import *
from ..websockets.utils import player_connections, get_players_id
from ..players.schemas import PlayerRol
from ..players.utils import find_player_by_id
from ..cards.utils import find_card_by_id
from ..cards.schemas import CardType, CardSubtype


class Events(str, Enum):
    GAME_CREATED = 'game_created'
    GAME_UPDATED = 'game_updated'
    GAME_DELETED = 'game_deleted'
    GAME_STARTED = 'game_started'
    GAME_CANCELED = 'game_canceled'
    GAME_ENDED = 'game_ended'
    PLAYER_JOINED = 'player_joined'
    PLAYER_LEFT = 'player_left'
    PLAYER_INIT_HAND = 'player_init_hand'
    PLAYED_CARD = 'played_card'
    PLAYER_ELIMINATED = 'player_eliminated'
    WHISKEY_CARD_PLAYED = 'whiskey_card_played'
    PLAYER_DRAW_CARD = 'player_draw_card'
    NEW_TURN = 'new_turn'
    BETWEEN_US_CARD_PLAYED = 'between_us_card_played'
    ROUND_AND_ROUND_START = 'round_and_round_start'
    ROUND_AND_ROUND_END = 'round_and_round_end'
    REVELATIONS_CARD_PLAYED = 'revelations_card_played'
    REVELATIONS_SHOW = 'revelations_show'
    REVELATIONS_DONE = 'revelations_done'
    EXCHANGE_INTENTION = 'exchange_intention'
    EXCHANGE_DONE = 'exchange_done'
    BLIND_DATE_SELECTION = 'blind_date_selection'
    BLIND_DATE_DONE = 'blind_date_done'
    OOOPS_CARD_PLAYED = 'ooops_card_played'


@db_session
def find_game_by_name(game_name: str):
    game = Game.get(name=game_name)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

    return game


@db_session
def verify_game_can_start(name: str, host_player_id: int):
    game = find_game_by_name(name)
    players_joined = count(game.players)

    if game.status == GameStatus.STARTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The game has already started."
        )

    if not 4 <= players_joined <= 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The number of players joined ({players_joined}) is not allowed."
        )

    if game.host.id != host_player_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only the host player can start the game."
        )


@db_session
def verify_game_can_be_canceled(game_name: str, host_player_id: int):
    game = find_game_by_name(game_name)

    if game.status != GameStatus.UNSTARTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The game is not in unstarted status"
        )
    if game.host.id != host_player_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only the host player can cancel the game."
        )


@db_session
def verify_game_can_be_abandon(game_name: str, player_id: int):
    game = find_game_by_name(game_name)
    player = Player.get(id=player_id)

    if game.status != GameStatus.UNSTARTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The game is not in unstarted status"
        )
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    if player not in game.players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player not in the game"
        )
    if player == game.host:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Host of the game can only cancel the game"
        )


@db_session
def verify_game_can_be_finished(game: Game):
    if not (no_human_remains(game) or the_thing_is_eliminated(game)):
        raise Exception('There are living Humans and The Thing')


@db_session
def the_thing_is_eliminated(game: Game) -> bool:
    the_thing_exists = game.players.select(
        lambda p: p.rol == PlayerRol.THE_THING).exists()

    return not the_thing_exists


@db_session
def no_human_remains(game: Game) -> bool:
    the_thing_exists = game.players.select(
        lambda p: p.rol == PlayerRol.THE_THING).exists()

    number_of_humans = game.players.select(
        lambda p: p.rol == PlayerRol.HUMAN).count()

    return the_thing_exists and number_of_humans == 0


@db_session
def the_thing_infected_everyone(game: Game) -> bool:
    the_thing_exists = game.players.select(
        lambda p: p.rol == PlayerRol.THE_THING).exists()

    number_of_infecteds = game.players.select(
        lambda p: p.rol == PlayerRol.INFECTED).count()

    return the_thing_exists and number_of_infecteds == count(game.players) - 1


@db_session
def list_of_unstarted_games() -> List[GameResponse]:
    games = Game.select(lambda game: game.status !=
                        GameStatus.STARTED and game.status != GameStatus.ENDED)
    games_list = [GameResponse(
        name=game.name,
        min_players=game.min_players,
        max_players=game.max_players,
        host_player_id=game.host.id,
        status=game.status,
        is_private=game.password is not None,
        num_of_players=len(game.players)
    ) for game in games]
    return games_list


@db_session
def list_of_games() -> List[GameResponse]:
    games = Game.select()
    games_list = [GameResponse(
        name=game.name,
        min_players=game.min_players,
        max_players=game.max_players,
        host_player_id=game.host.id,
        status=game.status,
        is_private=game.password is not None,
        num_of_players=len(game.players)
    ) for game in games]
    return games_list


@db_session
async def send_initial_cards(game_name: str):
    playersID = get_players_id(game_name)

    for idx in playersID:
        player = Player.get(id=idx)
        hand_cards = [card.id for card in player.hand]
        json_msg = {
            "event": Events.PLAYER_INIT_HAND,
            "game_name": game_name,
            "player_id": player.id,
            "hand_cards": hand_cards
        }
        await player_connections.send_event_to(player_id=player.id, message=json_msg)


@db_session
def verify_discard_can_be_done(game_name: str, game_data: DiscardInformationIn):
    game = Game.get(name=game_name)
    player = Player.get(id=game_data.player_id)
    card = Card.get(id=game_data.card_id)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )

    is_player_in_game = select(
        p for p in game.players if (p.id == player.id)).exists()
    is_card_in_hand = select(
        c for c in player.hand if (c.id == card.id)).exists()

    if not is_player_in_game:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The player is not in the game"
        )
    if not is_card_in_hand:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The card doesn't belong to the player"
        )
    if card.type == CardType.THE_THING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The Thing cannot be discarded"
        )
    if game.turn != player.position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="It's not the turn of the player"
        )
    if player.rol == PlayerRol.INFECTED and card.name == '¡Infectado!':
        infected_count = select(count(c)
                                for c in player.hand if c.name == '¡Infectado!')
        if infected_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The player is infected and cannot discard the card"
            )


@db_session
def verify_player_in_game(player_id: int, game_name: str):
    player: Player = find_player_by_id(player_id)
    game: Game = find_game_by_name(game_name)
    if player and game:
        if player in game.players:
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The player is not in the game"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player or game not found"
        )


@db_session
def verify_adjacent_players(player_id: int, other_player_id: int, max_position: int):
    player = find_player_by_id(player_id)
    other_player = find_player_by_id(other_player_id)

    are_adjacent = (
        abs(player.position - other_player.position) == 1 or
        (player.position == 0 and other_player.position == max_position) or
        (other_player.position == 0 and player.position == max_position)
    )

    if not are_adjacent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Players are not adjacent"
        )


@db_session
def merge_decks_of_card(game_name: str):
    game: Game = find_game_by_name(game_name)
    top_card_id = game.draw_deck_order.pop(0)
    new_deck_list = list(game.draw_deck) + list(game.discard_deck)
    game.draw_deck.clear()
    game.discard_deck.clear()
    game.draw_deck_order = []
    game.draw_deck.add(new_deck_list)

    # A continuacion genero el orden aleatorio de como van a robarse las cartas
    for card in game.draw_deck:
        if card.id != top_card_id:
            game.draw_deck_order.append(card.id)
    random.shuffle(game.draw_deck_order)
    # Inserto primera la carta que quedaba en draw_deck
    game.draw_deck_order.insert(0, top_card_id)


@db_session
def verify_draw_can_be_done(game_name: str, game_data: DiscardInformationIn):
    game = find_game_by_name(game_name)
    player = find_player_by_id(game_data.player_id)
    verify_player_in_game(player_id=game_data.player_id, game_name=game_name)

    if game.status != GameStatus.STARTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The game status isn't STARTED"
        )

    if len(game.draw_deck) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The draw deck is empty"
        )

    if len(player.hand) > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The player already has 5 cards"
        )

    if game.turn != player.position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Is not the player turn"
        )


@db_session
def verify_player_is_next_in_turn(game_name: str, player_id: int, other_player_id: int):
    game = find_game_by_name(game_name)
    player = find_player_by_id(player_id)
    other_player = find_player_by_id(other_player_id)

    players_not_eliminated = select(
        p for p in game.players if p.rol != PlayerRol.ELIMINATED).count()

    if game.round_direction == RoundDirection.CLOCKWISE:
        next_turn = (player.position - 1) % players_not_eliminated
    else:
        next_turn = (player.position + 1) % players_not_eliminated

    if next_turn != other_player.position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The player selected is not the next in turn"
        )


@db_session
def verify_pass_card_can_be_done(game_name: str, play_info: PlayInformation):
    player: Player = find_player_by_id(play_info.player_id)
    card: Card = find_card_by_id(play_info.card_id)
    verify_player_in_game(play_info.player_id, game_name)
    verify_player_in_game(play_info.objective_player_id, game_name)
    verify_player_is_next_in_turn(
        play_info.player_id, play_info.objective_player_id)
    if card.type == CardType.THE_THING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The Thing cannot be passed"
        )
    is_card_in_player = select(
        c for c in player.hand if (c.id == card.id)).exists()
    if not is_card_in_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The card is not in the hand of the player"
        )


@db_session
def verify_player_is_next_in_turn(game_name: str, player_id: int, other_player_id: int):
    game = find_game_by_name(game_name)
    player = find_player_by_id(player_id)
    other_player = find_player_by_id(other_player_id)

    players_not_eliminated = select(
        p for p in game.players if p.rol != PlayerRol.ELIMINATED).count()

    if game.round_direction == RoundDirection.CLOCKWISE:
        next_turn = (player.position - 1) % players_not_eliminated
    else:
        next_turn = (player.position + 1) % players_not_eliminated

    if next_turn != other_player.position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The player selected is not the next in turn"
        )


@db_session
def verify_pass_card_can_be_done(game_name: str, play_info: PlayInformation):
    player: Player = find_player_by_id(play_info.player_id)
    card: Card = find_card_by_id(play_info.card_id)
    verify_player_in_game(play_info.player_id, game_name)
    verify_player_in_game(play_info.objective_player_id, game_name)
    verify_player_is_next_in_turn(
        play_info.player_id, play_info.objective_player_id)
    if card.type == CardType.THE_THING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The Thing cannot be passed"
        )
    is_card_in_player = select(
        c for c in player.hand if (c.id == card.id)).exists()
    if not is_card_in_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The card is not in the hand of the player"
        )


@db_session
def verify_if_interchange_can_be_done(game_name: str, interchange_info: IntentionExchangeInformationIn):
    game: Game = find_game_by_name(game_name)
    player: Player = find_player_by_id(interchange_info.player_id)
    card: Card = Card[interchange_info.card_id]

    if game.turn != player.position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Is not the player turn"
        )
    if card.type == CardType.THE_THING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The Thing cannot be interchange'
        )
    if card not in player.hand:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The card selected for the interchange is not in the player hand'
        )
    if card.subtype == CardSubtype.CONTAGION and player.rol != PlayerRol.THE_THING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The player cannot pass the card Infected because is not The Thing'
        )


@db_session
def verify_if_interchange_response_can_be_done(game_name: str, game_data: InterchangeInformationIn):
    game: Game = find_game_by_name(game_name)
    player: Player = find_player_by_id(game_data.player_id)
    player_card: Card = Card[game_data.card_id]
    objective_player: Player = find_player_by_id(game_data.objective_player_id)
    objective_player_card: Card = Card[game_data.objective_card_id]

    if not player_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Card of next player in turn not found'
        )
    if not objective_player_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Card of the player in turn not found'
        )
    if player_card.type == CardType.THE_THING or objective_player_card.type == CardType.THE_THING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The Thing cannot be interchange'
        )
    if player_card.type != CardType.STAY_AWAY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The card of the next player in turn must be a STAY_AWAY card'
        )
    if player_card not in player.hand:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The card selected for the interchange is not in the next player hand'
        )
    if objective_player_card not in objective_player.hand:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The card selected for the interchange is not in the player hand'
        )
    if not player in game.players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The next player in turn is not in the game'
        )
    if not objective_player in game.players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The player in turn is not in the game'
        )
    if player_card.subtype == CardSubtype.CONTAGION and player.rol != PlayerRol.THE_THING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Player next in turn cannot pass an infected card because is not The Thing'
        )


@db_session
def get_id_of_next_player_in_turn(game_name):
    game: Game = find_game_by_name(game_name)
    players_playing = len(
        list(select(p for p in game.players if p.rol != PlayerRol.ELIMINATED)))
    if game.round_direction == RoundDirection.CLOCKWISE:
        next_turn = (game.turn + 1) % players_playing
    else:
        next_turn = (game.turn - 1) % players_playing

    next_player_id = select(
        p.id for p in game.players if p.position == next_turn).first()
    return next_player_id


def is_the_game_finished(game_name: str) -> bool:
    game: Game = find_game_by_name(game_name)
    try:
        verify_game_can_be_finished(game)
        return True
    except:
        return False


@db_session
def update_game_turn(game_name: str):
    game: Game = find_game_by_name(game_name)
    players_playing = len(
        list(select(p for p in game.players if p.rol != PlayerRol.ELIMINATED)))
    if game.round_direction == RoundDirection.CLOCKWISE:
        game.turn = (game.turn + 1) % players_playing
    else:
        game.turn = (game.turn - 1) % players_playing
