from pydispatch import dispatcher


class View:
    def __init__(self):
        dispatcher.connect(self.print_to_console, signal="Put_Text")
        dispatcher.connect(self.show_choices, signal="Give_Choice")

    def print_to_console(self, sender, text: str):
        print(text)

    def show_choices(self, sender, choices: dict[str, bool]):
        while True:
            # Display the choices
            print(f"Your choices are: {", ".join(choices.keys())}")

            # Get the user's choice
            choice = input("Please enter a choice or type 'exit' to quit.")

            # Allow the user to exit
            if choice == "exit":
                dispatcher.send("Exit_Game", self)

            # Send valid choices to the interpreter
            elif choice in choices:
                dispatcher.send("Make_Choice", self, choice)

            print("Invalid choice, try again.\n")
