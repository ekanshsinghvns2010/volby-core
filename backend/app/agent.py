from .tools import TOOLS


class VolbyAgent:
    def __init__(self):
        self.name = "Volby Core"

    def think(self, message: str) -> str:
        message = message.strip()

        if not message:
            return "I didn't receive a command."

        if message.lower() == "check device":
            tool = TOOLS["device_status"]
            result = tool.execute()
            return f"Device status: {result}"

        return f"I received your command: {message}"

    def run(self, message: str) -> str:
        return self.think(message)