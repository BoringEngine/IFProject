import logging

from pydispatch import dispatcher

log = logging.getLogger("Interpreter")


class Interpreter:
    def __init__(self):
        dispatcher.connect(self.handle_choice, signal="Make_Choice")

        # Mock choices: True is a placeholder for Address
        self.choices = {"north": True, "south": True, "east": True, "west": True}

        self.last_choice = None

        log.debug("Interpreter initialized.")

    def step(self):
        """Run the interpreter one step"""
        # Pretend the interpreter has some logic to choose a direction
        log.debug("Sending Give_Choice signal.")
        dispatcher.send("Give_Choice", choices=self.choices)

    def handle_choice(self, choice: str):
        log.debug(f"Received choice: {choice}")

        # Store the last choice
        self.last_choice = choice
