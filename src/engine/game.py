import logging

from pydispatch import dispatcher

import engine.parser
from engine.interpreter import Interpreter
from engine.view import View

log = logging.getLogger("Game")


class Game:
    def __init__(self):
        log.debug("Inializing Interpreter.")
        self.interpreter = Interpreter()
        log.debug("Initializing View.")
        self.view = View()
        log.debug("Connecting signals.")
        dispatcher.connect(self.handle_exit, signal="Exit_Game")

    def run(self):
        """Run the interpreter until Exit_Game is dispatched."""
        log.debug("Game loop running.")
        step_count = 0
        while True:
            log.debug(f"Running step {step_count}.")
            self.interpreter.step()
            step_count += 1

    def handle_exit(self, sender):
        """Handle an Exit_Game event, cleanup and exit the game."""
        logging.debug("Received Exit_Game signal. Exiting game.")
        exit()
