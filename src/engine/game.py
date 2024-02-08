from pydispatch import dispatcher

import engine.parser
from engine.interpreter import Interpreter
from engine.view import View


class Game:
    def __init__(self):
        self.interpreter = Interpreter()
        self.view = View()
        dispatcher.connect(self.handle_exit, signal="Exit_Game")

    def start(self):
        self.interpreter.run()

    def handle_exit(self):
        # Do any cleanup here
        exit()
