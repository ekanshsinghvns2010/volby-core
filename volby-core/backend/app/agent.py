import json
import os
import requests

from .tools import TOOLS


class VolbyAgent:
    def __init__(self):
        self.name = "Volby Core"

        self.api_key = os.getenv("OPENROUTER_API_KEY")

        self.model = "openrouter/free"

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
You are the intent router for Volby Core,
an Android AI agent.

Your job is to understand the user's natural-language
request and select the correct tool.

AVAILABLE TOOLS:

1. device_status

Use ONLY when the user asks about their device,
phone connection, or device status.

Example:
"Is my phone connected?"

Return:
{{"intent":"device_status"}}


2. open_app

Use when the user wants to open or use an Android app.

Available apps include:

YouTube
WhatsApp
Instagram
Facebook
Messenger
Chrome
Google
Play Store
LinkedIn
Gmail
Google Maps
Google Photos
Google Drive
Google Meet
Google Calendar
Google Translate
YouTube Music
Spotify
Telegram
Snapchat
Reddit
Discord
X
Pinterest
Netflix
Amazon
Flipkart
PhonePe
Paytm
Zomato
Swiggy

Examples:

"I want to watch some videos"

Return:
{{"intent":"open_app","app":"YouTube"}}

"I need to message my friend"

Return:
{{"intent":"open_app","app":"WhatsApp"}}

"I want to browse the internet"

Return:
{{"intent":"open_app","app":"Chrome"}}


3. open_website

Use when the user specifically wants a website
opened.

Example:
"Open wikipedia.org"

Return:
{{"intent":"open_website","url":"https://wikipedia.org"}}


4. web_search

Use when the user wants to search for information.

Example:
"Search the web for the weather in Varanasi"

Return:
{{"intent":"web_search","query":"weather in Varanasi"}}


If no available tool matches:

Return:
{{"intent":"none"}}


IMPORTANT:

Understand the meaning of the request.

Do NOT require the user to use commands like
"open", "launch", or "search".

Return ONLY valid JSON.

Do not use markdown.
Do not explain your answer.

USER REQUEST:

{message}
"""

        try:

            response = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer":
                        "https://github.com/"
                        "ekanshsinghvns2010/volby-core",
                    "X-Title": "Volby Core"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content":
                                "You are a precise Android "
                                "tool-intent router."
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
                    "response":
                        f"Device status: {result}",
                    "action": None
                }

            # OPEN APP
            if intent == "open_app":

                app_name = decision.get("app")

                if not app_name:
                    return {
                        "response":
                            "I couldn't determine which app to open.",
                        "action": None
                    }

                tool = TOOLS["open_app"]

                action = tool.execute(
                    app_name=app_name
                )

                return {
                    "response":
                        f"Opening {app_name}...",
                    "action": action
                }

            # OPEN WEBSITE
            if intent == "open_website":

                url = decision.get("url")

                if not url:
                    return {
                        "response":
                            "I couldn't determine which website to open.",
                        "action": None
                    }

                tool = TOOLS["open_website"]

                action = tool.execute(
                    url=url
                )

                return {
                    "response":
                        f"Opening {url}...",
                    "action": action
                }

            # WEB SEARCH
            if intent == "web_search":

                query = decision.get("query")

                if not query:
                    return {
                        "response":
                            "I couldn't determine what to search for.",
                        "action": None
                    }

                tool = TOOLS["web_search"]

                action = tool.execute(
                    query=query
                )

                return {
                    "response":
                        f"Searching for {query}...",
                    "action": action
                }

            # NONE
            return {
                "response":
                    f"I received your command: {message}",
                "action": None
            }

        except json.JSONDecodeError:

            return {
                "response":
                    "AI returned an invalid decision.",
                "action": None
            }

        except requests.HTTPError as e:

            status = e.response.status_code

            try:
                error_body = e.response.text
            except Exception:
                error_body = ""

            return {
                "response":
                    f"OpenRouter HTTP error {status}: "
                    f"{error_body[:500]}",
                "action": None
            }

        except requests.RequestException as e:

            return {
                "response":
                    f"AI connection error: {str(e)}",
                "action": None
            }

        except Exception as e:

            return {
                "response":
                    f"AI processing error: {str(e)}",
                "action": None
            }

    def run(self, message: str):
        return self.think(message)