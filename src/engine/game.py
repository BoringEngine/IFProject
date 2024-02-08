from pydispatch import dispatcher

import engine.parser
from engine.interpreter import Interpreter
from engine.view import View


class Game:
    def __init__(self):
        self.interpreter = Interpreter()
        self.view = View()
        # self.story = ?

    def start(self):
        self.interpreter.run()
