"""
A console runner for the game engine.

Usage:
    $ python -m engine.main

Expected behavior:
    - The game displays choices: north, south, east, west, exit
    - The game waits for user input, and then displays the choices again
    - The game exits on "exit"
"""


import logging

import logging518.config

# Config logging before importing submodules
# Otherwise submodules get empty loggers
logging518.config.fileConfig("pyproject.toml")

from engine.game import Game

log = logging.getLogger("IFProject")


def main():
    log.info("Welcome to IFProject!")
    log.info("Loading the game.")
    game = Game()

    log.info("Runing the game loop.")
    game.run()


if __name__ == "__main__":
    main()
