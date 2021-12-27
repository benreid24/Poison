from typing import List
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
