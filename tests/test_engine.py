from unittest.mock import patch

import pytest
from engine.game import Game
from pydispatch import dispatcher


@pytest.fixture
def loaded_game():
    yield Game()


@pytest.fixture
def sample_choices():
    return {"args": "yargs"}


@pytest.fixture
def mock_exit():
    """Prevent program termination during tests."""
    with patch("builtins.exit") as mock:
        yield mock


@pytest.fixture
def mock_show_choices():
    """Prevent view side effects during tests, and capture call args for testing."""
    with patch("engine.view.View.show_choices") as mock:
        yield mock


class TestGame:
    def test_game_loads(self, loaded_game):
        """Given a loaded Game,
        Then the View and Interpreter are loaded"""
        assert loaded_game.view is not None
        assert loaded_game.interpreter is not None

    class TestEvents:
        def test_exit_game(self, mock_exit, loaded_game):
            """Given a loaded Game,
            When an Exit_Game event fires,
            Then Game exits the program"""
            dispatcher.send(signal="Exit_Game")

            mock_exit.assert_called_once()

        def test_give_choice(self, mock_show_choices, sample_choices, loaded_game):
            """Given a loaded Game,
            When a Give_Choice event fires,
            Then the view choice update fires"""
            dispatcher.send(signal="Give_Choice", choices=sample_choices)

            mock_show_choices.assert_called_once()
            assert mock_show_choices.call_args.kwargs["choices"] == sample_choices

        def test_make_choice(self, loaded_game):
            """Given a loaded Game,
            When a Make_Choice event fires,
            Then the interpreter updates its last_choice attribute"""
            choice = "choice"
            dispatcher.send(signal="Make_Choice", choice=choice)

            assert loaded_game.interpreter.last_choice == choice
