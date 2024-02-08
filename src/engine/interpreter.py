from pydispatch import dispatcher


class Interpreter:
    def __init__(self):
        dispatcher.connect(self.handle_choice, signal="Make_Choice")

        # Mock choices: True is a placeholder for Address
        self.choices = {"north": True, "south": True, "east": True, "west": True}

    def step(self):
        """Run the interpreter one step"""
        # Pretend the interpreter has some logic to choose a direction
        dispatcher.send("Give_Choice", self, self.choices)

    def handle_choice(self, sender, choice: str):
        ...  # Currently, we don't do anything with the choice
