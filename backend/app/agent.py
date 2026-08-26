from .tools import TOOLS


class VolbyAgent:
    def __init__(self):
        self.name = "Volby Core"

    def think(self, message: str):
        message = message.strip()

        if not message:
            return {
                "response": "I didn't receive a command."
            }

        lower = message.lower()

        # Device status tool
        if lower == "check device":
            tool = TOOLS["device_status"]
            result = tool.execute()

            return {
                "response": f"Device status: {result}"
            }

        # Open-app intent
        app_name = self.extract_app_name(lower)

        if app_name:
            tool = TOOLS["open_app"]
            action = tool.execute(app_name=app_name)

            return {
                "response": f"Opening {app_name}...",
                "action": action
            }

        return {
            "response": f"I received your command: {message}"
        }

    def extract_app_name(self, message: str):
        prefixes = [
            "open ",
            "launch ",
            "start ",
            "run "
        ]

        for prefix in prefixes:
            if message.startswith(prefix):
                app_name = message[len(prefix):].strip()

                if app_name:
                    return app_name

        phrases = [
            "can you open ",
            "please open ",
            "could you open ",
            "can you launch ",
            "please launch ",
            "could you launch "
        ]

        for phrase in phrases:
            if phrase in message:
                app_name = message.split(phrase, 1)[1].strip()

                if app_name:
                    return app_name

        return None

    def run(self, message: str):
        return self.think(message)