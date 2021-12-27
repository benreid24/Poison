from enum import Enum
from typing import List

from django.db import models


class DataModelException(Exception):
    pass


class Player(models.Model):
    name = models.TextField(max_length=64)


class GamePlayer(models.Model):
    index = models.IntegerField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    cards = models.CharField(max_length=104)

    class Meta:
        ordering = ['index']


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
    Ave = 'a'
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
            if len(data) != 2:
                raise DataModelException(f'Bad card id: {data}')
            try:
                self.type = CardType(data[0])
                self.suit = CardSuit(data[1])
            except ValueError:
                raise DataModelException(f'Unknown card id: {data}')
        else:
            self.type = kind
            self.suit = suit

    def is_red(self):
        return self.suit == CardSuit.Hearts or self.suit == CardSuit.Diamonds

    def __str__(self):
        return f'{self.type.value}{self.suit.value}'

    @staticmethod
    def get_cards(cards):
        # type: (str) -> List[Card]
        
        if len(cards) % 2 != 0:
            raise DataModelException(f'Bad length card array: {cards}')
        
        split = [cards[i:i+2] for i in range(0, len(cards), 2)]
        return [Card(s) for s in split]


class GameAction(models.Model):
    class Type(models.IntegerChoices):
        PlayerJoined = 1
        PlayerLeft = 2
        CardPlayed = 3
        PoisonCalled = 4

    index  = models.IntegerField()
    action = models.IntegerField(choices=Type.choices)
    player = models.ForeignKey(GamePlayer, on_delete=models.CASCADE)
    data   = models.CharField(max_length=256)

    class Meta:
        ordering = ['index']


class Game(models.Model):
    center_deck = models.TextField(max_length=104)
    left_deck   = models.TextField(max_length=104)
    right_deck  = models.TextField(max_length=104)
    players     = models.ForeignKey(GamePlayer, on_delete=models.CASCADE)
    turn        = models.IntegerField()
    actions     = models.ForeignKey(GameAction, on_delete=models.CASCADE)
