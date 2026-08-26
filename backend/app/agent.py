class VolbyAgent:
    def __init__(self):
        self.name = "Volby Core"

    def think(self, message: str) -> str:
        message = message.strip()

        if not message:
            return "I didn't receive a command."

        return f"I received your command: {message}"

    def run(self, message: str) -> str:
        return self.think(message)