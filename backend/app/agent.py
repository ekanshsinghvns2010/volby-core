import json
import os
import requests

from .tools import TOOLS


class VolbyAgent:
    def __init__(self):
        self.name = "Volby Core"

        self.api_key = os.getenv("OPENROUTER_API_KEY")

        self.model = "meta-llama/llama-3.2-1b-instruct"

        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def think(self, message: str):

        message = message.strip()

        if not message:
            return {
                "response": "I didn't receive a command."
            }

        if not self.api_key:
            return {
                "response": "AI configuration is missing."
            }

        prompt = f"""
You are the intent router for Volby Core, an Android AI agent.

Available tools:

1. device_status
Description: Check whether the Android device is connected.

2. open_app
Description: Open an installed Android application.

User request:
{message}

Determine what the user wants.

Return ONLY valid JSON.

For a device status request:
{{
  "intent": "device_status"
}}

For an app-opening request:
{{
  "intent": "open_app",
  "app": "YouTube"
}}

If no available tool matches:
{{
  "intent": "none"
}}

Do not include markdown.
Do not include explanations.
"""

        try:

            response = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a precise tool-intent classifier."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0
                },
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

            content = data["choices"][0]["message"]["content"]

            decision = json.loads(content)

            intent = decision.get("intent")

            if intent == "device_status":

                tool = TOOLS["device_status"]

                result = tool.execute()

                return {
                    "response": f"Device status: {result}"
                }

            if intent == "open_app":

                app_name = decision.get("app")

                if not app_name:
                    return {
                        "response": "I couldn't determine which app you want to open."
                    }

                tool = TOOLS["open_app"]

                action = tool.execute(
                    app_name=app_name
                )

                return {
                    "response": f"Opening {app_name}...",
                    "action": action
                }

            return {
                "response": f"I received your command: {message}"
            }

        except Exception as e:

            return {
                "response": f"AI processing error: {str(e)}"
            }

    def run(self, message: str):
        return self.think(message)