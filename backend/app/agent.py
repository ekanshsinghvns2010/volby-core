import json
import os
import requests

from .tools import TOOLS


class VolbyAgent:
    def __init__(self):
        self.name = "Volby Core"

        self.api_key = os.getenv("OPENROUTER_API_KEY")

        self.model = "openai/gpt-oss-20b:free"

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

Available apps include:
YouTube
WhatsApp
Instagram
Facebook
Chrome
Google
Play Store
LinkedIn
Gmail
Maps
Gallery
Camera
Calculator
Settings

User request:
{message}

Determine what the user wants.

IMPORTANT:
If the request can be fulfilled by opening an installed app,
use the open_app intent.

Examples:

"Open YouTube"
→
{{
  "intent": "open_app",
  "app": "YouTube"
}}

"I want to watch some videos"
→
{{
  "intent": "open_app",
  "app": "YouTube"
}}

"I need to message someone"
→
{{
  "intent": "open_app",
  "app": "WhatsApp"
}}

"I want to browse the internet"
→
{{
  "intent": "open_app",
  "app": "Chrome"
}}

"I want to check Instagram"
→
{{
  "intent": "open_app",
  "app": "Instagram"
}}

"I need to search something on Google"
→
{{
  "intent": "open_app",
  "app": "Google"
}}

"I want to check my email"
→
{{
  "intent": "open_app",
  "app": "Gmail"
}}

"Is my phone connected?"
→
{{
  "intent": "device_status"
}}

If no available tool can fulfill the request:
{{
  "intent": "none"
}}

Return ONLY valid JSON.

Do not use markdown.
Do not explain your answer.
Do not add any text outside the JSON.
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
                            "content": (
                                "You are a precise intent classifier "
                                "for an Android AI agent."
                            )
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

            content = data["choices"][0]["message"]["content"].strip()

            decision = json.loads(content)

            intent = decision.get("intent")

            if intent == "device_status":

                tool = TOOLS["device_status"]

                result = tool.execute()

                return {
                    "response": f"Device status: {result}",
                    "action": None
                }

            if intent == "open_app":

                app_name = decision.get("app")

                if not app_name:
                    return {
                        "response": (
                            "I couldn't determine which app "
                            "you want to open."
                        ),
                        "action": None
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
                "response": f"I received your command: {message}",
                "action": None
            }

        except json.JSONDecodeError:

            return {
                "response": "The AI returned an invalid decision.",
                "action": None
            }

        except requests.RequestException as e:

            return {
                "response": f"AI connection error: {str(e)}",
                "action": None
            }

        except Exception as e:

            return {
                "response": f"AI processing error: {str(e)}",
                "action": None
            }

    def run(self, message: str):
        return self.think(message)