from typing import List, Iterable
from random import shuffle

from django.core.exceptions import BadRequest

from .models import Card, CardSuit, CardType, Game, GamePlayer, Player


def make_deck():
    # type: () -> List[Card]
    return [Card(kind=t, suit=s) for t in CardType for s in CardSuit]


def encode_deck(deck):
    # type: (List[Card]) -> str
    return ''.join([str(c) for c in deck])


def encode_game(game, player_key):
    # type: (Game, str) -> dict

    try:
        gp = GamePlayer.objects.get(game__pk=game.key, player__pk=player_key)
        return {
            'key': game.key,
            'turn': game.turn,
            'player_key': player_key,
            'player_index': gp.index,
            'cards': gp.cards,
            'left_card': game.left_deck[0:2],
            'right_card': game.right_deck[0:2]
        }
    except Exception:
        raise BadRequest(f'Invalid player id: {player_key}')


def create_game(player_id):
    # type: (str) -> Game

    try:
        player = Player.objects.get(pk=player_id)
    except Player.DoesNotExist:
        raise BadRequest(f'Bad player id: {player_id}')

    deck = make_deck()
    shuffle(deck)
    game = Game(
        center_deck=encode_deck(deck[2:]),
        left_deck=encode_deck(deck[0:1]),
        right_deck=encode_deck(deck[1:2]),
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
        raise BadRequest('Game already started')

    gps = GamePlayer.objects.filter(game__pk=game_id)
    if len(gps) >= 6:
        raise BadRequest('Game is full')
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
            raise BadRequest('Only the host may start the game')
    except Game.DoesNotExist:
        raise BadRequest(f'Bad game id: {game_id}')
    except GamePlayer.DoesNotExist:
        raise BadRequest('Not in game')

    if g.turn >= 0:
        raise BadRequest('Game already started')

    gps = GamePlayer.objects.filter(game__pk=game_id) # type: Iterable[GamePlayer]
    if len(gps) < 2:
        raise BadRequest('Not enough players')
    
    g.turn = 0
    deck = Card.get_cards(g.center_deck)
    for _ in range(0, 7):
        for p in gps:
            card = deck.pop(0)
            p.cards += str(card)
    g.center_deck = encode_deck(deck)

    for p in gps:
        p.save()
    g.save()

    return g
