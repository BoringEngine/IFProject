from pydispatch import dispatcher
from engine.interpreter import Interpreter
from engine.view import View
import engine.parser

class Game:
    def __init__(self):
        self.interpreter = Interpreter()
        self.view = View()
        # self.story = ?
    
    def start(self):
        self.interpreter.run()