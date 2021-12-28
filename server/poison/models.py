from enum import Enum
from typing import List
from base64 import b32encode
from hashlib import sha1
from random import random

from django.db import models
from django.core.exceptions import BadRequest, FieldError

PK_LEN = 16


def gen_key():
    # type: () -> str
    return sha1(str(random()).encode('utf-8')).hexdigest().upper()[:PK_LEN]


class Player(models.Model):
    key = models.CharField(max_length=PK_LEN, primary_key=True, default=gen_key)
    name = models.TextField(max_length=64)


class CardType(Enum):
    One = '1'
    Two = '2'
    Three = '3'
    Four = '4'
    Five = '5'
    Six = '6'
    Seven = '7'
    Eight = '8'
    Nine = '9'
    Ten = '0'
    Jack = 'j'
    Queen = 'q'
    King = 'k'
    Ace = 'a'
    Joker = 'x'


class CardSuit(Enum):
    Spades = 's'
    Hearts = 'h'
    Clubs = 'c'
    Diamonds = 'd'


class Card:
    def __init__(self, data=None, kind=None, suit=None):
        # type: (str, CardType, CardSuit) -> None

        if data:
            if not isinstance(data, str):
                raise BadRequest(f'Invalid card id: {data}')
            if len(data) != 2:
                raise BadRequest(f'Invalid card id: {data}')
            try:
                self.type = CardType(data[0])
                self.suit = CardSuit(data[1])
            except ValueError:
                raise BadRequest(f'Unknown card id: {data}')
        else:
            self.type = kind
            self.suit = suit

    def is_red(self):
        return self.suit == CardSuit.Hearts or self.suit == CardSuit.Diamonds

    def is_face(self):
        return self.type in [CardType.Jack, CardType.Queen, CardType.King, CardType.Ace]

    def __str__(self):
        return f'{self.type.value}{self.suit.value}'

    @staticmethod
    def get_deck(cards):
        # type: (str) -> List[Card]
        
        if len(cards) % 2 != 0:
            raise FieldError(f'Bad length card array: {cards}')
        
        split = [cards[i:i+2] for i in range(0, len(cards), 2)]
        return [Card(s) for s in split]

    @staticmethod
    def encode_deck(deck):
        # type: (List[Card]) -> str
        return ''.join([str(c) for c in deck])


class Game(models.Model):
    key         = models.CharField(max_length=PK_LEN, primary_key=True, default=gen_key)
    center_deck = models.TextField(max_length=104)
    left_deck   = models.TextField(max_length=104)
    right_deck  = models.TextField(max_length=104)
    turn        = models.IntegerField()

    @staticmethod
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
                'right_card': game.right_deck[0:2],
                'left_count': len(game.left_deck) / 2,
                'right_count': len(game.right_deck) / 2,
                'center_count': len(game.center_deck) / 2
            }
        except Exception:
            raise BadRequest(f'Invalid player id: {player_key}')


class GamePlayer(models.Model):
    index  = models.IntegerField()
    game   = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    cards  = models.CharField(max_length=104, default='')

    class Meta:
        ordering = ['index']
        indexes = [
            models.Index(fields=['game', 'player'])
        ]


class GameAction(models.Model):
    class Type(models.IntegerChoices):
        CardPlayed = 1
        CardDrawn = 2
        PoisonCalled = 3

    index  = models.IntegerField()
    action = models.IntegerField(choices=Type.choices)
    game   = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(GamePlayer, on_delete=models.CASCADE)
    data   = models.CharField(max_length=256)

    class Meta:
        ordering = ['-index']
