import copy
from hsgame.agents.basic_agents import DoNothingBot
from hsgame.constants import CHARACTER_CLASS
from tests.testing_agents import SpellTestingAgent
from tests.testing_utils import generate_game_for
from hsgame.cards import StonetuskBoar

__author__ = 'Daniel'
import random
import unittest
from unittest.mock import Mock, call

from hsgame.game_objects import Player, Game, Deck, Bindable, card_lookup, SecretCard

import hsgame.cards


class TestGame(unittest.TestCase):

    def setUp(self):
        random.seed(1857)

    def test_create_game(self):
        card_set1 = []
        card_set2 = []
        test_env = self

        for cardIndex in range(0, 30):
            card_set1.append(card_lookup("Stonetusk Boar"))
            card_set2.append(card_lookup("Novice Engineer"))

        deck1 = Deck(card_set1, CHARACTER_CLASS.DRUID)
        deck2 = Deck(card_set2, CHARACTER_CLASS.MAGE)
        checked_cards = []

        class MockAgent1:
            def do_card_check(self, cards):

                test_env.assertEqual(len(cards), 3)
                checked_cards.append(list(cards))
                return [False, True, True]

            def set_game(self, game):
                pass

        class MockAgent2:
            def do_card_check(self, cards):

                test_env.assertEqual(len(cards), 4)
                checked_cards.append(list(cards))
                return [False, True, True, False]

            def set_game(self, game):
                pass

        agent1 = unittest.mock.Mock(spec=MockAgent1(), wraps=MockAgent1())
        agent2 = unittest.mock.Mock(spec=MockAgent2(), wraps=MockAgent2())
        game = Game([deck1, deck2], [agent1, agent2])
        game.pre_game()
        self.assertEqual(agent1.method_calls[0][0], "set_game", "Agent not asked to select cards")
        self.assertEqual(agent2.method_calls[0][0], "set_game", "Agent not asked to select cards")

        self.assertEqual(agent1.method_calls[1][0], "do_card_check", "Agent not asked to select cards")
        self.assertEqual(agent2.method_calls[1][0], "do_card_check", "Agent not asked to select cards")

        self.assertTrue(game.players[0].deck == deck1, "Deck not assigned to player")
        self.assertTrue(game.players[1].deck == deck2, "Deck not assigned to player")

        self.assertTrue(game.players[0].agent == agent1, "Agent not stored in the hsgame")
        self.assertTrue(game.players[1].agent == agent2, "Agent not stored in the hsgame")

        self.assertListEqual(checked_cards[0][1:], game.players[0].hand[:-1], "Cards not retained after request")
        self.assertListEqual(checked_cards[1][1:2], game.players[1].hand[:-3], "Cards not retained after request")

    def test_first_turn(self):
        card_set1 = []
        card_set2 = []
        test_env = self

        for cardIndex in range(0, 30):
            card_set1.append(card_lookup("Stonetusk Boar"))
            card_set2.append(card_lookup("Novice Engineer"))

        deck1 = Deck(card_set1, CHARACTER_CLASS.DRUID)
        deck2 = Deck(card_set2, CHARACTER_CLASS.MAGE)

        agent1 = unittest.mock.Mock(spec=DoNothingBot(), wraps=DoNothingBot())
        agent2 = unittest.mock.Mock(spec=DoNothingBot(), wraps=DoNothingBot())
        game = Game([deck1, deck2], [agent1, agent2])

        game.start()

    def test_secrets(self):
        for secret_type in SecretCard.__subclasses__():
            random.seed(1857)
            secret = secret_type()
            game = generate_game_for(secret_type, StonetuskBoar, SpellTestingAgent, DoNothingBot)
            for turn in range(0, secret.mana * 2 - 2):
                game.play_single_turn()

            def assert_different():
                new_events = copy.copy(game.events)
                new_events.update(game.other_player.events)
                new_events.update(game.current_player.events)
                self.assertNotEqual(events, new_events, secret.name)

            def assert_same():
                new_events = copy.copy(game.events)
                new_events.update(game.current_player.events)
                new_events.update(game.other_player.events)
                self.assertEqual(events, new_events)

            game.current_player.bind("turn_ended", assert_different)
            game.other_player.bind("turn_ended", assert_same)

            #save the events as they are prior to the secret being played
            events = copy.copy(game.events)
            events.update(game.other_player.events)
            events.update(game.current_player.events)

            #The secret is played, but the events aren't updated until the secret is activated
            game.play_single_turn()

            self.assertEqual(1, len(game.current_player.secrets))

            #Now the events should be changed
            game.play_single_turn()

            #Now the events should be reset
            game.play_single_turn()




class TestBinding(unittest.TestCase):

    def test_bind(self):
        event = Mock()
        binder = Bindable()
        binder.bind("test", event)
        binder.trigger("test", 1, 5, 6, arg1="something", args2="whatever")
        event.assert_called_once_with(1, 5, 6, arg1="something", args2="whatever")
        binder.unbind("test", event)
        binder.trigger("test")
        event.assert_called_once_with(1, 5, 6, arg1="something", args2="whatever")

    def test_bind_once(self):
        event = Mock()
        event2 = Mock()
        binder = Bindable()
        binder.bind_once("test", event)
        binder.bind("test", event2)
        binder.trigger("test", 1, 5, 6, arg1="something", args2="whatever")
        event.assert_called_once_with(1, 5, 6, arg1="something", args2="whatever")
        event2.assert_called_once_with(1, 5, 6, arg1="something", args2="whatever")
        binder.trigger("test")
        event.assert_called_once_with(1, 5, 6, arg1="something", args2="whatever")
        self.assertEqual(event2.call_count, 2)

    def test_bind_with_different_args(self):
        event = Mock()
        event2 = Mock()
        binder = Bindable()
        binder.bind("test", event, 5)
        binder.bind("test", event2)
        binder.trigger("test")
        event.assert_called_with(5)
        event2.assert_called_with()



