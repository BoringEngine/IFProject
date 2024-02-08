"""
A console runner for the game engine.

Usage:
    $ python -m engine.main

Expected behavior:
    - The game displays choices: north, south, east, west, exit
    - The game waits for user input, and then displays the choices again
    - The game exits on "exit"
"""


from engine.game import Game


def main():
    game = Game()
    game.start()
