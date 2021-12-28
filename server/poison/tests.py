from typing import Tuple

from django.test import TestCase

from .exceptions import (
    BadTurnException,
    GameAlreadStartedException,
    GameFullException,
    InvalidCardPlayException,
    MissingCardException,
    NoPlaysYetException,
    NotEnoughPlayersException,
    NotHostException,
    NotInGameException,
    OutOfCardsException,
    PoisonAlreadyCalledException
)
from .models import Game, GameAction, GamePlayer, Player
from . import game, actions


class GamePlayTests(TestCase):
    @staticmethod
    def _create_game():
        # type: () -> Tuple[Game, GamePlayer, GamePlayer]
        p1 = Player.objects.create(name='Ben') # type: Player
        p2 = Player.objects.create(name='Anna') # type: Player

        g = game.create_game(p1.key)
        g = game.join_game(g.key, p2.key)
        g = game.start_game(g.key, p1.key)
        return (
            g,
            GamePlayer.objects.get(game__pk=g.key, player__pk=p1.key),
            GamePlayer.objects.get(game__pk=g.key, player__pk=p2.key)
        )

    def test_createand_start_game(self):
        p1 = Player.objects.create(name='Ben') # type: Player
        p2 = Player.objects.create(name='Anna') # type: Player
        g = game.create_game(p1.key)

        with self.assertRaises(NotEnoughPlayersException):
            game.start_game(g.key, p1.key)

        g = game.join_game(g.key, p2.key)

        ps = GamePlayer.objects.filter(game__pk=g.key)
        self.assertEqual(len(ps), 2)
        self.assertEqual(ps[0].player.key, p1.key)
        self.assertEqual(ps[1].player.key, p2.key)

        for _ in range(4):
            g = game.join_game(g.key, Player.objects.create(name='another').key)
        with self.assertRaises(GameFullException):
            game.join_game(g.key, Player.objects.create(name='rejected').key)

        with self.assertRaises(NotHostException):
            game.start_game(g.key, p2.key)
        with self.assertRaises(NotInGameException):
            game.start_game(g.key, Player.objects.create(name='outsider').key)

        g = game.start_game(g.key, p1.key)
        self.assertEqual(len(g.center_deck), (54-6*7-2)*2)
        self.assertEqual(len(g.left_deck), 2)
        self.assertEqual(len(g.right_deck), 2)
        ps = GamePlayer.objects.filter(game__pk=g.key)
        for p in ps:
            self.assertEqual(len(p.cards), 14)

        with self.assertRaises(GameAlreadStartedException):
            game.join_game(g.key, Player.objects.create(name='rejected').key)
        with self.assertRaises(GameAlreadStartedException):
            game.start_game(g.key, p1.key)

    def test_draw_cards(self):
        g, p1, p2 = GamePlayTests._create_game()

        # No shuffle
        g.center_deck = 'ahqcxh'
        g.left_deck = '2d5c'
        g.right_deck = '7skh'
        p2.cards = ''
        actions._draw_cards(g, p2, 2)
        self.assertEqual(g.left_deck, '2d5c')
        self.assertEqual(g.right_deck, '7skh')
        self.assertEqual(len(g.center_deck), 2)
        self.assertEqual(len(p2.cards), 4)
        c = 0
        for s in ['ah', 'qc', 'xh']:
            if s in p2.cards:
                c += 1
        self.assertEqual(c, 2)

        # Shuffling
        g.center_deck = 'ah'
        g.left_deck = '2d5c'
        g.right_deck = '7skh'
        p1.cards = ''
        actions._draw_cards(g, p1, 3)
        self.assertEqual(g.left_deck, '2d')
        self.assertEqual(g.right_deck, '7s')
        self.assertEqual(len(g.center_deck), 0)
        self.assertEqual(len(p1.cards), 6)
        self.assertTrue('ah' in p1.cards)
        self.assertTrue('5c' in p1.cards)
        self.assertTrue('kh' in p1.cards)

        # Not enough cards
        g.center_deck = 'ah'
        g.left_deck = '2d5c'
        g.right_deck = '7skh'
        p1.cards = ''
        with self.assertRaises(OutOfCardsException):
            actions._draw_cards(g, p1, 4)

        # Through an action
        g.center_deck = 'ah'
        g.left_deck = '2d5c'
        g.right_deck = '7skh'
        p1.cards = ''
        g.turn = 0
        g.save()
        p1.save()
        p2.save()
        g = game.perform_action(g.key, p1.player.key, GameAction.Type.CardDrawn, {})
        self.assertEqual(len(g.center_deck), 4)
        p1 = GamePlayer.objects.get(game__pk=g.key, player__pk=p1.player.key)
        self.assertEqual(p1.cards, 'ah')
        aq = GameAction.objects.filter(game__pk=g.key)
        self.assertEqual(len(aq), 1)
        self.assertEqual(aq[0].action, GameAction.Type.CardDrawn)

    def test_legal_card_playing(self):
        g, p1, p2 = GamePlayTests._create_game()

        def reload():
            nonlocal g
            nonlocal p1
            nonlocal p2
            g = Game.objects.get(pk=g.key)
            p1 = GamePlayer.objects.get(game__pk=g.key, player__pk=p1.player.key)
            p2 = GamePlayer.objects.get(game__pk=g.key, player__pk=p2.player.key)

        # Adjacent same color
        g.right_deck = 'ah'
        p1.cards = '2d5s'
        g.save()
        p1.save()
        game.perform_action(g.key, p1.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': '2d'})
        reload()
        self.assertEqual(g.right_deck, '2dah')
        self.assertEqual(p1.cards, '5s')
        self.assertEqual(len(p2.cards), 18) # drew 2
        self.assertEqual(len(g.center_deck), 72)

        # Adjacent different color
        g.left_deck = '7h'
        p2.cards = '8cxh'
        g.save()
        p2.save()
        game.perform_action(g.key, p2.player.key, GameAction.Type.CardPlayed, {'side': 'left', 'card': '8c'})
        reload()
        self.assertEqual(g.left_deck, '8c7h')
        self.assertEqual(p2.cards, 'xh')

        # Face card on number
        g.right_deck = '8c'
        p1.cards = 'ksxh'
        g.save()
        p1.save()
        game.perform_action(g.key, p1.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': 'ks'})
        reload()
        self.assertEqual(g.right_deck, 'ks8c')
        self.assertEqual(p1.cards, 'xh')

        # Face card on face card
        g.right_deck = 'jc'
        p2.cards = 'ksxh'
        g.save()
        p2.save()
        game.perform_action(g.key, p2.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': 'ks'})
        reload()
        self.assertEqual(g.right_deck, 'ksjc')
        self.assertEqual(p1.cards, 'xh')

        # Color on face card
        g.right_deck = 'kd'
        p1.cards = '8hxh'
        g.save()
        p1.save()
        game.perform_action(g.key, p1.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': '8h'})
        reload()
        self.assertEqual(g.right_deck, '8hkd')
        self.assertEqual(p1.cards, 'xh')

        # Joker on face card
        g.right_deck = 'kd'
        p2.cards = '8hxh'
        g.save()
        p2.save()
        game.perform_action(g.key, p2.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': 'xh'})
        reload()
        self.assertEqual(g.right_deck, 'xhkd')
        self.assertEqual(p2.cards, '8h')

        # Face card on joker
        g.right_deck = 'xd'
        p1.cards = '8hkh'
        g.save()
        p1.save()
        game.perform_action(g.key, p1.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': 'kh'})
        reload()
        self.assertEqual(g.right_deck, 'khxd')
        self.assertEqual(p1.cards, '8h')

    def test_illegal_card_playing(self):
        g, p1, p2 = GamePlayTests._create_game()

        # Non-adjacent numbers
        g.right_deck = '8h'
        p1.cards = 'xh3d'
        g.save()
        p1.save()
        with self.assertRaises(InvalidCardPlayException):
            game.perform_action(g.key, p1.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': '3d'})

        # Non-adjacent face cards
        g.right_deck = 'kh'
        p1.cards = 'xhjs'
        g.save()
        p1.save()
        with self.assertRaises(InvalidCardPlayException):
            game.perform_action(g.key, p1.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': 'js'})

        # Joker on number
        g.right_deck = '8h'
        p1.cards = 'xhjs'
        g.save()
        p1.save()
        with self.assertRaises(InvalidCardPlayException):
            game.perform_action(g.key, p1.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': 'xh'})

        # Number on joker
        g.right_deck = 'xh'
        p1.cards = 'xh3s'
        g.save()
        p1.save()
        with self.assertRaises(InvalidCardPlayException):
            game.perform_action(g.key, p1.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': '3s'})

        # Joker on joker
        g.right_deck = 'xh'
        p1.cards = 'xhjs'
        g.save()
        p1.save()
        with self.assertRaises(InvalidCardPlayException):
            game.perform_action(g.key, p1.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': 'xh'})

        # Number on self
        g.right_deck = '8h'
        p1.cards = 'xh8d'
        g.save()
        p1.save()
        with self.assertRaises(InvalidCardPlayException):
            game.perform_action(g.key, p1.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': '8d'})

        # Face card on self
        g.right_deck = 'jh'
        p1.cards = 'xhjc'
        g.save()
        p1.save()
        with self.assertRaises(InvalidCardPlayException):
            game.perform_action(g.key, p1.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': 'jc'})

    def test_call_poison(self):
        g, p1, p2 = GamePlayTests._create_game()

        def reload():
            nonlocal g
            nonlocal p1
            nonlocal p2
            g = Game.objects.get(pk=g.key)
            p1 = GamePlayer.objects.get(game__pk=g.key, player__pk=p1.player.key)
            p2 = GamePlayer.objects.get(game__pk=g.key, player__pk=p2.player.key)

        p1.cards = '9h0hxd'
        g.right_deck = '8h'
        p2.cards = '4c5dxh'
        g.left_deck = '3c'
        g.save()
        p1.save()
        p2.save()

        game.perform_action(g.key, p1.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': '9h'})
        game.perform_action(g.key, p2.player.key, GameAction.Type.CardPlayed, {'side': 'left', 'card': '4c'})
        game.perform_action(g.key, p1.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': '0h'})

        # Actual poison
        game.perform_action(g.key, p2.player.key, GameAction.Type.PoisonCalled, {})
        reload()
        self.assertEqual(len(p1.cards), 8)
        self.assertEqual(len(g.center_deck), (54-2*7-2-3)*2)

        # Incorrect poison
        game.perform_action(g.key, p2.player.key, GameAction.Type.CardPlayed, {'side': 'left', 'card': '5d'})
        game.perform_action(g.key, p2.player.key, GameAction.Type.PoisonCalled, {}) # on self lol, but not on own turn
        reload()
        self.assertEqual(len(p2.cards), 8)
        self.assertEqual(len(g.center_deck), (54-2*7-2-6)*2)

    def test_bad_actions(self):
        g, p1, p2 = GamePlayTests._create_game()

        p1.cards = 'xhkd'
        p2.cards = '4hac'
        g.left_deck = 'kd'
        p1.save()
        p2.save()
        g.save()

        with self.assertRaises(BadTurnException):
            game.perform_action(g.key, p2.player.key, GameAction.Type.CardDrawn, {})

        with self.assertRaises(NoPlaysYetException):
            game.perform_action(g.key, p2.player.key, GameAction.Type.PoisonCalled, {})

        with self.assertRaises(MissingCardException):
            game.perform_action(g.key, p1.player.key, GameAction.Type.CardPlayed, {'side': 'right', 'card': '4d'})

        game.perform_action(g.key, p1.player.key, GameAction.Type.CardPlayed, {'side': 'left', 'card': 'xh'})
        aq = GameAction.objects.filter(game__pk=g.key)
        self.assertEqual(len(aq), 1)
        self.assertEqual(aq[0].action, GameAction.Type.CardPlayed)
        print('here')
        game.perform_action(g.key, p2.player.key, GameAction.Type.PoisonCalled, {})

        with self.assertRaises(BadTurnException):
            game.perform_action(g.key, p1.player.key, GameAction.Type.CardDrawn, {})

        with self.assertRaises(PoisonAlreadyCalledException):
            game.perform_action(g.key, p2.player.key, GameAction.Type.PoisonCalled, {})
