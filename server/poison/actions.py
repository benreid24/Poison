from typing import List, Iterable
from random import shuffle
import json

from .models import CardType, Game, GameAction, GamePlayer, Card
from .exceptions import (
    InvalidCardPlayException,
    MissingCardException,
    NoPlaysYetException,
    OutOfCardsException,
    PoisonAlreadyCalledException,
    UnknownException
)

CARD_TO_INT = {
    CardType.Ace: 0,
    CardType.One: 1,
    CardType.Two: 2,
    CardType.Three: 3,
    CardType.Four: 4,
    CardType.Five: 5,
    CardType.Six: 6,
    CardType.Seven: 7,
    CardType.Eight: 8,
    CardType.Nine: 9,
    CardType.Ten: 10,
    CardType.Jack: 11,
    CardType.Queen: 12,
    CardType.King: 13,
    CardType.Joker: -1,
}


def _draw_cards(game, player, n):
    # type: (Game, GamePlayer, int) -> None
    deck = Card.get_deck(game.center_deck)
    if len(deck) <= n:
        right = Card.get_deck(game.right_deck)
        left = Card.get_deck(game.left_deck)
        deck.extend(right[1:])
        deck.extend(left[1:])
        if len(deck) < n:
            raise OutOfCardsException()
        shuffle(deck)
        game.left_deck = Card.encode_deck([left[0]])
        game.right_deck = Card.encode_deck([right[0]])

    player.cards += Card.encode_deck(deck[0:n])
    game.center_deck = Card.encode_deck(deck[n:])


def _card_index(deck, card):
    # type: (List[Card], Card) -> int
    for i in range(0, len(deck)):
        if deck[i].type == card.type and deck[i].suit == card.suit:
            return i
    return -1


def _is_adjacent(c1, c2):
    # type: (Card, Card) -> bool
    if c1.type == CardType.Joker or c2.type == CardType.Joker:
        return False
    i1 = CARD_TO_INT[c1.type]
    i2 = CARD_TO_INT[c2.type]
    if abs(i2 - i1) == 1:
        return True
    if c1.type == CardType.Ace and c2.type == CardType.King:
        return True
    if c1.type == CardType.King and c2.type == CardType.Ace:
        return True
    return False


def play_card(game, player, card, is_right):
    # type: (Game, GamePlayer, Card, bool) -> None
    pile = Card.get_deck(game.right_deck if is_right else game.left_deck)
    top = pile[0]
    hand = Card.get_deck(player.cards)
    
    index = _card_index(hand, card)
    if index < 0:
        raise MissingCardException()

    if top.type == CardType.Joker:
        if not card.is_face():
            raise InvalidCardPlayException()
    
    if card.type == CardType.Joker:
        if not top.is_face():
            raise InvalidCardPlayException()

    if not _is_adjacent(card, top):
        if top.is_face() or card.is_face():
            if top.is_red() != card.is_red():
                raise InvalidCardPlayException()
        else:
            raise InvalidCardPlayException()

    if is_right:
        game.right_deck = Card.encode_deck([card, *pile])
    else:
        game.left_deck = Card.encode_deck([card, *pile])
    hand.pop(index)
    player.cards = Card.encode_deck(hand)

    players = GamePlayer.objects.filter(game__pk=game.key) # type: Iterable[GamePlayer]
    ni = (game.turn + 1) % len(players)
    if card.type == CardType.Two:
        _draw_cards(game, players[ni], 2)
        players[ni].save()
        # TODO - report what happened
    elif card.type == CardType.Ace:
        ni = (ni + 1) % len(players)
        # TODO - report what happened
    game.turn = ni
    

def draw_card(game, player):
    # type: (Game, GamePlayer) -> None
    _draw_cards(game, player, 1)


def call_poison(game, player):
    # type: (Game, GamePlayer) -> None
    players = GamePlayer.objects.filter(game__pk=game.key) # type: Iterable[GamePlayer]
    li = game.turn - 1 if game.turn > 0 else len(players) - 1
    last_player = players[li] # type: GamePlayer
    actions = GameAction.objects.filter(game__pk=game.key) # type: Iterable[GameAction]

    for action in actions:
        if action.action == GameAction.Type.PoisonCalled:
            raise PoisonAlreadyCalledException()
        if action.action == GameAction.Type.CardPlayed:
            if action.player.player.key != last_player.player.key:
                raise UnknownException('Last player to play is not consistent with turn order')
            is_right = json.loads(action.data)['side'] == 'right'
            cards = game.right_deck if is_right else game.left_deck
            deck = Card.get_deck(cards)
            if len(deck) >= 3:
                for i in range(1, 3):
                    if deck[i].is_red() != deck[i-1].is_red():
                        return # TODO - return what happened
                _draw_cards(game, last_player, 3)
                last_player.save()
                return # TODO - return what happened

    raise NoPlaysYetException()
