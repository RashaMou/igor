import asyncio
import sys


class Console:
    def __init__(self, hub):
        self.hub = hub

    def start_listening(self):
        while True:
            user_input = self.async_input("listening... \n")
            if user_input == "q":
                sys.exit()

            print(f"you said: {user_input}")

    @staticmethod
    def async_input(prompt):
        # to thread runs the input method in a separate thread because it is a
        # blocking call and would otherwise block the asyncio event loop
        return (input, prompt)
