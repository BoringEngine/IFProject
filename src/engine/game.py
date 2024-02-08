from pydispatch import dispatcher

import engine.parser
from engine.interpreter import Interpreter
from engine.view import View


class Game:
    def __init__(self):
        self.interpreter = Interpreter()
        self.view = View()
        dispatcher.connect(self.handle_exit, signal="Exit_Game")

    def run(self):
        """Run the interpreter until Exit_Game is dispatched."""
        while True:
            self.interpreter.step()

    def handle_exit(self, sender):
        """Handle an Exit_Game event, cleanup and exit the game."""
        exit()
