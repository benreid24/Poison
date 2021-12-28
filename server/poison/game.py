from typing import List, Iterable
from random import shuffle
import json

from django.core import exceptions
from django.core.exceptions import BadRequest

from .models import Card, CardSuit, CardType, Game, GamePlayer, Player, GameAction
from .exceptions import (
    BadTurnException,
    GameAlreadStartedException,
    GameFullException,
    NotInGameException,
    NotEnoughPlayersException,
    NotHostException
)
from .actions import play_card, draw_card, call_poison


def make_deck():
    # type: () -> List[Card]
    return [Card(kind=t, suit=s) for t in CardType for s in CardSuit]


def create_game(player_id):
    # type: (str) -> Game

    try:
        player = Player.objects.get(pk=player_id)
    except Player.DoesNotExist:
        raise BadRequest(f'Bad player id: {player_id}')

    deck = make_deck()
    shuffle(deck)
    game = Game(
        center_deck=Card.encode_deck(deck[2:]),
        left_deck=Card.encode_deck(deck[0:1]),
        right_deck=Card.encode_deck(deck[1:2]),
        turn=-1,
    )
    game.save()

    gp = GamePlayer(index=0, game=game, player=player)
    gp.save()

    return game


def join_game(game_id, player_id):
    # type: (str, str) -> Game

    try:
        g = Game.objects.get(pk=game_id) # type: Game
        player = Player.objects.get(pk=player_id)
    except Game.DoesNotExist:
        raise BadRequest(f'Bad game id: {game_id}')
    except Player.DoesNotExist:
        raise BadRequest(f'Bad player id: {player_id}')

    if g.turn >= 0:
        raise GameAlreadStartedException()

    gps = GamePlayer.objects.filter(game__pk=game_id)
    if len(gps) >= 6:
        raise GameFullException()
    for gp in gps:
        if gp.player.key == player_id:
            return g
    
    gp = GamePlayer(index=len(gps), game=g, player=player)
    gp.save()
    return g


def start_game(game_id, player_id):
    # type: (str, str) -> Game

    try:
        g = Game.objects.get(pk=game_id) # type: Game
        player = GamePlayer.objects.get(game__pk=game_id, player__pk=player_id)
        if player.index != 0:
            raise NotHostException()
    except Game.DoesNotExist:
        raise BadRequest(f'Bad game id: {game_id}')
    except GamePlayer.DoesNotExist:
        raise NotInGameException()

    if g.turn >= 0:
        raise GameAlreadStartedException()

    gps = GamePlayer.objects.filter(game__pk=game_id) # type: Iterable[GamePlayer]
    if len(gps) < 2:
        raise NotEnoughPlayersException()
    
    g.turn = 0
    deck = Card.get_deck(g.center_deck)
    for _ in range(0, 7):
        for p in gps:
            card = deck.pop(0)
            p.cards += str(card)
    g.center_deck = Card.encode_deck(deck)

    for p in gps:
        p.save()
    g.save()

    return g


def perform_action(game_id, player_id, kind, params):
    # type: (str, str, GameAction.Type, dict) -> Game
    try:
        g = Game.objects.get(pk=game_id) # type: Game
        p = GamePlayer.objects.get(game__pk=game_id, player__pk=player_id) # type: GamePlayer
    except Game.DoesNotExist:
        raise BadRequest(f'Bad game id: {game_id}')
    except GamePlayer.DoesNotExist:
        raise BadRequest(f'Bad player id: {player_id}')

    if g.turn != p.index and kind != GameAction.Type.PoisonCalled:
        raise BadTurnException()

    try:
        if kind == GameAction.Type.CardPlayed:
            card = params['card']
            is_right = params['side'] == 'right'
            play_card(g, p, Card(card), is_right)
        elif kind == GameAction.Type.CardDrawn:
            draw_card(g, p)
        elif kind == GameAction.Type.PoisonCalled:
            call_poison(g, p)
    except KeyError as e:
        raise BadRequest(f'Missing required param: {e}')

    actions = GameAction.objects.filter(game__pk=game_id)
    a = GameAction(
        index=len(actions),
        action=kind,
        game=g,
        player=p,
        data=json.dumps(params)
    )

    a.save()
    g.save()
    p.save()
    return g
