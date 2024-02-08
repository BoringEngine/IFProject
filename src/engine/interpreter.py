from pydispatch import dispatcher


class Interpreter:
    def __init__(self):
        dispatcher.connect(self.handle_choice, signal="Make_Choice")

        # Mock choices: True is a placeholder for Address
        self.choices = {"north": True, "south": True, "east": True, "west": True}

    def run(self):
        # Keep running steps until we return False
        # (meaning we should wait for user input)
        while self.step():
            pass

        dispatcher.send("Give_Choice", self, self.choices)

    def handle_choice(self, sender, choice: str):
        self.address = self.choice_to_address(choice)
        self.run()
