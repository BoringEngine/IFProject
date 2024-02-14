import logging

from pydispatch import dispatcher

log = logging.getLogger("View")


class View:
    def __init__(self):
        dispatcher.connect(self.print_to_console, signal="Put_Text")
        dispatcher.connect(self.show_choices, signal="Give_Choice")
        log.debug("View initialized.")

    def print_to_console(self, text: str):
        print(text)

    def show_choices(self, choices: dict[str, bool]):
        log.debug(f"Received choices: {choices}")
        while True:
            # Display the choices
            print(f"Your choices are: {", ".join(choices.keys())}")

            # Get the user's choice
            choice = input("Please enter a choice or type 'exit' to quit.\n" "=>  ")
            choice = choice.lower().strip()  # Fix spaces and case

            log.debug(f"Received choice: {choice}")

            # Allow the user to exit
            if choice == "exit":
                log.debug("Sending Exit_Game signal.")
                dispatcher.send("Exit_Game", self)

            # Send valid choices to the interpreter
            elif choice in choices:
                log.debug(f"Sending Make_Choice signal with choice: {choice}")
                dispatcher.send("Make_Choice", choice=choice)
                return

            log.debug("Invalid choice, retrying.")
            print("Invalid choice, try again.\n")
