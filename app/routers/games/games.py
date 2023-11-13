from fastapi import APIRouter, status
from pony.orm import db_session, select
from app.database.models import Player
from . import services
from . import utils
from .schemas import *
from ..websockets.utils import player_connections
from .utils import find_game_by_name, is_the_game_finished, Events, send_played_card_event
from ..players.utils import get_player_name_by_id, find_player_by_id
from ..cards.utils import get_card_name_by_id, get_card_type_by_id, is_flamethrower, is_whiskey
from .services import finish_game
from .intention import *
from .defense_functions import ActionType


router = APIRouter(
    prefix="/games",
    tags=["games"],
)


@router.get("/", response_model=list[GameResponse], status_code=status.HTTP_200_OK)
def get_unstarted_games():
    return services.get_unstarted_games()


@router.get("/{game_name}", response_model=GameInformationOut, status_code=status.HTTP_200_OK)
def get_game_information(game_name: str):
    return services.get_game_information(game_name)


@router.get("/{game_name}/result")
def get_game_result(game_name: str) -> GameResult:
    return services.get_game_result(game_name)


@router.post("/", response_model=GameCreationOut, status_code=status.HTTP_201_CREATED)
async def create_game(game_data: GameCreationIn):
    new_game = services.create_game(game_data)

    json_msg = {
        "event": utils.Events.GAME_CREATED,
        "game_name": new_game.name
    }
    await player_connections.broadcast(json_msg)

    return new_game


@router.patch("/{name}/init")
async def start(name: str, host_player_id: int) -> GameStartOut:
    utils.verify_game_can_start(name, host_player_id)
    game = services.start_game(name)

    await utils.send_initial_cards(name)

    json_msg = {
        "event": utils.Events.GAME_STARTED,
        "game_name": name
    }
    await player_connections.broadcast(json_msg)

    return game


@router.patch("/{game_name}", response_model=GameUpdateOut, status_code=status.HTTP_200_OK)
async def update_game(game_name: str, game_data: GameUpdateIn):
    game_updated = services.update_game(game_name, game_data)

    json_msg = {
        "event": utils.Events.GAME_UPDATED,
        "game_name": game_name
    }
    await player_connections.broadcast(json_msg)

    return game_updated


@router.delete("/{game_name}", status_code=status.HTTP_200_OK)
async def delete_game(game_name: str):
    services.delete_game(game_name)

    json_msg = {
        "event": utils.Events.GAME_DELETED,
        "game_name": game_name
    }
    await player_connections.broadcast(json_msg)

    return {"message": "Game deleted"}


@router.patch("/join/{game_name}", response_model=GameInformationOut, status_code=status.HTTP_200_OK)
async def join_player(game_name: str, game_data: GameInformationIn):
    game = services.join_player(game_name, game_data)

    json_msg = {
        "event": utils.Events.PLAYER_JOINED,
        "player_id": game_data.player_id,
        "game_name": game.name
    }
    await player_connections.broadcast(json_msg)

    return game


@router.delete("/cancel/{game_name}", status_code=status.HTTP_200_OK)
async def cancel_game(game_name: str, player_id: int):
    utils.verify_game_can_be_canceled(game_name, player_id)

    json_msg = {
        "event": utils.Events.GAME_CANCELED,
        "game_name": game_name
    }
    await player_connections.send_event_to_other_players_in_game(game_name=game_name,
                                                                 message=json_msg,
                                                                 excluded_id=player_id)

    services.cancel_game(game_name)

    json_msg["event"] = utils.Events.GAME_DELETED
    await player_connections.broadcast(message=json_msg)

    return {"message": "Game canceled"}


@router.patch("/leave/{game_name}", response_model=GameInformationOut, status_code=status.HTTP_200_OK)
async def leave_game(game_name: str, player_id: int):
    utils.verify_game_can_be_abandon(game_name, player_id)
    json_msg = {
        "event": utils.Events.PLAYER_LEFT,
        "game_name": game_name
    }
    await player_connections.send_event_to_other_players_in_game(game_name=game_name,
                                                                 message=json_msg,
                                                                 excluded_id=player_id)

    gameInformation = services.leave_game(game_name, player_id)

    json_msg["event"] = utils.Events.GAME_UPDATED

    await player_connections.broadcast(message=json_msg)

    return gameInformation


@router.patch("/{game_name}/discard", status_code=status.HTTP_200_OK)
async def discard_card(game_name: str, game_data: DiscardInformationIn):
    utils.verify_discard_can_be_done(game_name, game_data)
    game = services.discard_card(game_name, game_data)
    with db_session:
        player_id_turn = select(
            p for p in game.players if p.position == game.turn).first().id

    json_msg = {
        "event": Events.DISCARD_CARD,
        "player_name": get_player_name_by_id(game_data.player_id),
        "player_id": game_data.player_id,
        "card_type": get_card_type_by_id(game_data.card_id)
    }
    await player_connections.send_event_to_all_players_in_game(game_name, json_msg)
    return {"message": "Card discarded"}


@router.post("/{game_name}/play-action-card", status_code=status.HTTP_200_OK)
async def play_action_card(game_name: str, play_info: PlayInformation):
    result = services.play_action_card(game_name, play_info)

    if is_the_game_finished(game_name):
        await finish_game(game_name)
    else:
        await send_played_card_event(
            game_name, play_info.player_id, play_info.card_id)

    return result


@router.post("/{game_name}/play-panic-card", status_code=status.HTTP_200_OK)
async def play_panic_card(game_name: str, play_info: PlayInformation):
    result = services.play_panic_card(game_name, play_info)
    if is_the_game_finished(game_name):
        await finish_game(game_name)
    else:
        await send_played_card_event(
            game_name, play_info.player_id, play_info.card_id)

    return result


@router.patch("/{game_name}/draw-card", status_code=status.HTTP_200_OK, response_model=CardResponse)
async def draw_card(game_name: str, game_data: DrawInformationIn):
    utils.verify_draw_can_be_done(game_name, game_data)
    draw_card_information = services.draw_card(game_name, game_data)

    json_msg = {
        "event": utils.Events.PLAYER_DRAW_CARD,
        "game_name": game_name,
        "player_name": get_player_name_by_id(game_data.player_id),
        "player_id": game_data.player_id,
        "next_card": draw_card_information.top_card_face
    }

    await player_connections.send_event_to_all_players_in_game(game_name=game_name,
                                                               message=json_msg)

    return draw_card_information.card


@router.patch("/{game_name}/pass-card", status_code=status.HTTP_200_OK)
async def pass_card(game_name: str, play_info: PlayInformation):
    result = {"message": "pass card completed"}
    utils.verify_pass_card_can_be_done(game_name, play_info)
    services.pass_card(play_info)

    json_msg = {
        "event": utils.Events.ROUND_AND_ROUND_END
    }
    await player_connections.send_event_to(play_info.objective_player_id, json_msg)

    return result


@router.patch("/{game_name}/intention-to-interchange-card", status_code=status.HTTP_200_OK)
async def intention_to_interchange_card(game_name: str, interchange_info: IntentionExchangeInformationIn):
    utils.verify_if_interchange_can_be_done(game_name, interchange_info)
    objective_player_id = utils.get_id_of_next_player_in_turn(game_name)

    services.register_card_exchange_intention(
        game_name, interchange_info.player_id, interchange_info.card_id, objective_player_id)
    
    return {"message": "Card interchange intention terminated."}


@router.patch("/{game_name}/card-interchange-response", status_code=status.HTTP_200_OK)
async def card_interchange_response(game_name: str, game_data: InterchangeInformationIn):
    # services.card_interchange_response(game_name, game_data)
    with db_session:
        intention: Intention = get_intention_in_game(game_name)
        game: Game = find_game_by_name(game_name)

        player = find_player_by_id(intention.player.id)
        objective_player = find_player_by_id(intention.objective_player.id)

        player_card = find_card_by_id(intention.exchange_payload['card_id'])
        objective_player_card = find_card_by_id(game_data.card_id)
        interchange_verify_data = {
            "player_id": game_data.player_id,
            "card_id": game_data.card_id,
            "objective_player_id": objective_player.id,
            "objective_card_id": objective_player_card.id
        }
        interchange_verify = InterchangeInformationVerify(
            **interchange_verify_data)
    utils.verify_if_interchange_response_can_be_done(
        game_name, interchange_verify)
    services.update_game_turn(game_name)

    with db_session:
        intention: Intention = get_intention_in_game(game_name)
        game: Game = find_game_by_name(game_name)

        player = find_player_by_id(intention.player.id)
        objective_player = find_player_by_id(intention.objective_player.id)

        player_card = find_card_by_id(intention.exchange_payload['card_id'])
        objective_player_card = find_card_by_id(game_data.card_id)

        process_card_exchange(game, player, objective_player,
                              player_card, objective_player_card)

    clean_intention_in_game(game_name)

    with db_session:
        json_msg = {
            "event": utils.Events.EXCHANGE_DONE,
            "player_name": get_player_name_by_id(player.id),
            "objective_player_name": get_player_name_by_id(objective_player.id)
        }
        await player_connections.send_event_to_all_players_in_game(game_name, json_msg)

    with db_session:
        game = find_game_by_name(game_name)
        player_id_turn = select(
            p for p in game.players if p.position == game.turn).first().id

    json_msg = {
        "event": utils.Events.NEW_TURN,
        "next_player_name": get_player_name_by_id(player_id_turn),
        "next_player_id": player_id_turn,
        "round_direction": game.round_direction
    }
    await player_connections.send_event_to_all_players_in_game(game_name, json_msg)
    return {"message": "Card interchange terminated."}


@router.post("/{game_name}/show-revelations-cards/{player_id}", status_code=status.HTTP_200_OK)
async def show_revelations_cards(game_name: str, player_id: int, game_data: ShowRevelationsCardsIn):
    utils.verify_player_in_game(player_id, game_name)
    utils.verify_player_in_game(game_data.original_player_id, game_name)
    services.show_cards(game_name, player_id, game_data)
    if player_id == game_data.original_player_id:
        json_msg = {
            "event": utils.Events.REVELATIONS_DONE
        }
        await player_connections.send_event_to(player_id, json_msg)
    return {"message": "Show card terminated."}


@router.patch("/{game_name}/blind-date-interchange", status_code=status.HTTP_200_OK)
async def blind_date_interchange(game_name: str, game_data: IntentionExchangeInformationIn):
    utils.verify_player_in_game(game_data.player_id, game_name)
    services.blind_date_interchange(game_name, game_data)
    json_msg = {
        "event": utils.Events.BLIND_DATE_DONE
    }
    await player_connections.send_event_to(game_data.player_id, json_msg)
    return {"message": "Blind date interchange terminated."}


@router.patch("/{game_name}/forgetful-exchange", status_code=status.HTTP_200_OK)
async def card_forgetful_exchange(game_name: str, game_data: ForgetfulExchangeIn):
    utils.verify_player_in_game(game_data.player_id, game_name)
    services.card_forgetful_exchange(game_name, game_data)
    json_msg = {
        "event": utils.Events.FORGETFUL_DONE
    }
    await player_connections.send_event_to(game_data.player_id, json_msg)

    return {"message": "Forgetful exchange terminated"}


@router.patch("/{game_name}/one-two-effect", status_code=status.HTTP_200_OK)
async def card_one_two_effect(game_name: str, game_data: OneTwoEffectIn):
    utils.verify_player_in_game(game_data.player_id, game_name)
    utils.verify_player_in_game(game_data.objective_player_id, game_name)
    services.card_one_two_effect(game_data)
    json_msg = {
        "event": utils.Events.ONE_TWO_DONE
    }
    await player_connections.send_event_to_all_players_in_game(game_name, json_msg)

    return {"message": "One two effect terminated"}


@router.patch("/{game_name}/resolute-exchange", status_code=status.HTTP_200_OK)
async def card_resolute_exchange(game_name: str, game_data: ResoluteExchangeIn):
    utils.verify_player_in_game(game_data.player_id, game_name)
    services.card_resolute_exchange(game_name, game_data)
    json_msg = {
        "event": utils.Events.RESOLUTE_DONE
    }
    await player_connections.send_event_to(game_data.player_id, json_msg)

    return {"message": "Resolute exchange terminated"}


@router.post("/{game_name}/play-defense-card")
async def play_defense_card(game_name: str, defense_info: PlayDefenseInformation):
    utils.verify_defense_card_can_be_played(game_name, defense_info)
    intention: Intention = get_intention_in_game(game_name)
    defense = False
    if defense_info.card_id:
        services.play_defense_card(game_name, defense_info)

        json_msg = {
            "event": utils.Events.DEFENSE_CARD_PLAYED,
            "card_id": defense_info.card_id,
            "player_id": intention.player.id,
            "objective_player_id": intention.objective_player.id,
            "action_type": intention.action_type
        }
        if 73 <= defense_info.card_id and defense_info.card_id <= 76:
            card_name = get_card_name_by_id(
                intention.exchange_payload["card_id"])
            json_msg["card_to_exchange"] = card_name
        await player_connections.send_event_to_all_players_in_game(game_name, json_msg)
        defense = True
    else:
        process_intention_in_game(game_name)
        if is_the_game_finished(game_name):
            await finish_game(game_name)

    if (defense or intention.action_type != ActionType.EXCHANGE_OFFER):
        clean_intention_in_game(game_name)

    if (defense and intention.action_type == ActionType.EXCHANGE_OFFER):
        services.update_game_turn(game_name)
        with db_session:
            game = find_game_by_name(game_name)
            player_id_turn = select(
                p for p in game.players if p.position == game.turn).first().id

        json_msg = {
            "event": utils.Events.NEW_TURN,
            "next_player_name": get_player_name_by_id(player_id_turn),
            "next_player_id": player_id_turn,
            "round_direction": game.round_direction
        }
        await player_connections.send_event_to_all_players_in_game(game_name, json_msg)


@router.patch("/{game_name}/the-thing-end-game")
async def the_thing_end_game(game_name: str, game_data: TheThingEndGameIn):
    utils.verify_player_is_the_thing(game_data.player_id, game_name)
    services.finish_game_by_the_thing(game_name)

    json_msg = {
        "event": utils.Events.GAME_ENDED
    }
    await player_connections.send_event_to_all_players_in_game(game_name, json_msg)

    return {"message": "The thing ended the game"}
