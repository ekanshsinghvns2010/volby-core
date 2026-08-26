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
                "response": "I didn't receive a command.",
                "action": None
            }

        if not self.api_key:
            return {
                "response": "AI configuration is missing.",
                "action": None
            }

        prompt = f"""
You are the AI intent router for Volby Core, an Android AI agent.

Your job is to understand the user's request and select the correct
available tool.

AVAILABLE TOOLS:

device_status
- Use ONLY when the user is asking about whether their Android device
  is connected, online, available, or its device status.

open_app
- Use when the user wants to open, launch, start, use, or access an
  Android application.
- You must identify the most appropriate app.

Available apps:

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

IMPORTANT EXAMPLES:

User: "I want to watch some videos"
Answer:
{{"intent":"open_app","app":"YouTube"}}

User: "I'm bored, let me watch YouTube"
Answer:
{{"intent":"open_app","app":"YouTube"}}

User: "I need to message my friend"
Answer:
{{"intent":"open_app","app":"WhatsApp"}}

User: "I want to browse the web"
Answer:
{{"intent":"open_app","app":"Chrome"}}

User: "Take me to Instagram"
Answer:
{{"intent":"open_app","app":"Instagram"}}

User: "I want to search something"
Answer:
{{"intent":"open_app","app":"Google"}}

User: "Open LinkedIn"
Answer:
{{"intent":"open_app","app":"LinkedIn"}}

User: "Is my phone connected?"
Answer:
{{"intent":"device_status"}}

User: "Hello"
Answer:
{{"intent":"none"}}

CRITICAL RULE:
Do NOT use device_status for general requests.
Only use device_status when the user explicitly wants device
connection/status information.

Return ONLY valid JSON.

USER REQUEST:
{message}
"""

        try:

            response = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/ekanshsinghvns2010/volby-core",
                    "X-Title": "Volby Core"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a precise Android "
                                "tool-intent router."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0
                },
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            choices = data.get("choices")

            if not choices:
                return {
                    "response": "AI returned no result.",
                    "action": None
                }

            content = choices[0]["message"]["content"].strip()

            # Remove accidental markdown fences.
            if content.startswith("```"):
                content = content.replace("```json", "")
                content = content.replace("```", "")
                content = content.strip()

            decision = json.loads(content)

            intent = decision.get("intent")

            # DEVICE STATUS
            if intent == "device_status":

                tool = TOOLS["device_status"]

                result = tool.execute()

                return {
                    "response": f"Device status: {result}",
                    "action": None
                }

            # OPEN APP
            if intent == "open_app":

                app_name = decision.get("app")

                if not app_name:
                    return {
                        "response": "I couldn't determine which app to open.",
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

            # NOTHING MATCHED
            return {
                "response": f"I received your command: {message}",
                "action": None
            }

        except json.JSONDecodeError:

            return {
                "response": "AI returned an invalid decision.",
                "action": None
            }

        except requests.HTTPError as e:

            status = e.response.status_code

            try:
                error_body = e.response.text
            except Exception:
                error_body = ""

            return {
                "response": (
                    f"OpenRouter HTTP error {status}: "
                    f"{error_body[:500]}"
                ),
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