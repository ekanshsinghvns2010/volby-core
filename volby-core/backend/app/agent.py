import json
import os
import re
import requests

from .tools import TOOLS


class VolbyAgent:

    def __init__(self):
        self.name = "Volby Core"

        self.api_key = os.getenv("OPENROUTER_API_KEY")

        self.model = "openrouter/free"

        self.url = "https://openrouter.ai/api/v1/chat/completions"

    # --------------------------------------------------
    # WEBSITE DETECTION
    # --------------------------------------------------

    def detect_website(self, message):

        text = message.strip()

        patterns = [
            r"(?:open|visit|go to)\s+"
            r"(https?://[^\s]+)",
            
            r"(?:open|visit|go to)\s+"
            r"([a-zA-Z0-9-]+\.(?:com|org|net|in|io)(?:/[^\s]*)?)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                url = match.group(1)

                if not url.startswith("http://") and \
                   not url.startswith("https://"):

                    url = "https://" + url

                return url

        return None

    # --------------------------------------------------
    # SEARCH DETECTION
    # --------------------------------------------------

    def detect_search(self, message):

        text = message.strip()

        prefixes = [
            "search the web for ",
            "search the internet for ",
            "search for ",
            "look up "
        ]

        for prefix in prefixes:

            if text.lower().startswith(prefix):

                query = text[len(prefix):].strip()

                if query:

                    return query

        return None

    # --------------------------------------------------
    # FALLBACK INTENT
    # --------------------------------------------------

    def fallback_intent(self, message):

        text = message.lower().strip()

        # Website

        website = self.detect_website(message)

        if website:

            return {
                "intent": "open_website",
                "url": website
            }

        # Search

        search = self.detect_search(message)

        if search:

            return {
                "intent": "web_search",
                "query": search
            }

        # Device

        device_phrases = [
            "is my phone connected",
            "is my device connected",
            "check my device",
            "check device",
            "device status",
            "phone status"
        ]

        for phrase in device_phrases:

            if phrase in text:

                return {
                    "intent": "device_status"
                }

        # Apps

        apps = {

            "youtube": [
                "youtube",
                "watch videos",
                "watch a video",
                "watch something",
                "watch some videos"
            ],

            "whatsapp": [
                "whatsapp",
                "message my friend",
                "message someone",
                "send a message",
                "chat with my friend"
            ],

            "instagram": [
                "instagram",
                "check instagram",
                "look at reels"
            ],

            "facebook": [
                "facebook"
            ],

            "chrome": [
                "chrome",
                "browse the internet",
                "browse the web"
            ],

            "google": [
                "google"
            ],

            "gmail": [
                "gmail",
                "check my email",
                "check my emails"
            ],

            "linkedin": [
                "linkedin"
            ],

            "spotify": [
                "spotify",
                "listen to music"
            ],

            "telegram": [
                "telegram"
            ],

            "discord": [
                "discord"
            ],

            "netflix": [
                "netflix"
            ]
        }

        display_names = {
            "youtube": "YouTube",
            "whatsapp": "WhatsApp",
            "instagram": "Instagram",
            "facebook": "Facebook",
            "chrome": "Chrome",
            "google": "Google",
            "gmail": "Gmail",
            "linkedin": "LinkedIn",
            "spotify": "Spotify",
            "telegram": "Telegram",
            "discord": "Discord",
            "netflix": "Netflix"
        }

        for app_name, phrases in apps.items():

            for phrase in phrases:

                if phrase in text:

                    return {
                        "intent": "open_app",
                        "app":
                            display_names.get(
                                app_name,
                                app_name.title()
                            )
                    }

        return {
            "intent": "none"
        }

    # --------------------------------------------------
    # ASK AI
    # --------------------------------------------------

    def ask_ai(self, message):

        prompt = f"""
You are Volby Core's intent router.

Understand the user's request.

Available intents:

device_status
open_app
open_website
web_search
none

Rules:

- Use open_app when the user wants an Android application.
- Use open_website when the user wants a website.
- Use web_search when the user explicitly wants to search.
- Use device_status for device connection/status requests.
- Otherwise use none.

Examples:

I want to watch videos
{{"intent":"open_app","app":"YouTube"}}

I need to message my friend
{{"intent":"open_app","app":"WhatsApp"}}

Open Chrome
{{"intent":"open_app","app":"Chrome"}}

Open wikipedia.org
{{"intent":"open_website","url":"https://wikipedia.org"}}

Search the web for cricket news
{{"intent":"web_search","query":"cricket news"}}

Is my phone connected?
{{"intent":"device_status"}}

Return ONLY valid JSON.

User:
{message}
"""

        response = requests.post(
            self.url,
            headers={
                "Authorization":
                    f"Bearer {self.api_key}",
                "Content-Type":
                    "application/json",
                "HTTP-Referer":
                    "https://github.com/"
                    "ekanshsinghvns2010/volby-core",
                "X-Title":
                    "Volby Core"
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content":
                            "Return only valid JSON."
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

        choices = data.get(
            "choices",
            []
        )

        if not choices:
            return None

        content = (
            choices[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        content = content.replace(
            "```json",
            ""
        )

        content = content.replace(
            "```",
            ""
        )

        content = content.strip()

        try:

            return json.loads(content)

        except json.JSONDecodeError:

            match = re.search(
                r"\{.*\}",
                content,
                re.DOTALL
            )

            if match:

                try:

                    return json.loads(
                        match.group(0)
                    )

                except json.JSONDecodeError:
                    pass

        return None

    # --------------------------------------------------
    # EXECUTE INTENT
    # --------------------------------------------------

    def execute_intent(
            self,
            decision,
            message
    ):

        if not decision:

            decision = self.fallback_intent(
                message
            )

        intent = decision.get(
            "intent"
        )

        # DEVICE

        if intent == "device_status":

            result = TOOLS[
                "device_status"
            ].execute()

            return {
                "response":
                    f"Device status: {result}",
                "action": None
            }

        # APP

        if intent == "open_app":

            app_name = decision.get(
                "app"
            )

            if not app_name:

                decision = self.fallback_intent(
                    message
                )

                app_name = decision.get(
                    "app"
                )

            if not app_name:

                return {
                    "response":
                        "I couldn't determine which app to open.",
                    "action": None
                }

            action = TOOLS[
                "open_app"
            ].execute(
                app_name=app_name
            )

            return {
                "response":
                    f"Opening {app_name}...",
                "action": action
            }

        # WEBSITE

        if intent == "open_website":

            url = decision.get(
                "url"
            )

            if not url:

                decision = self.fallback_intent(
                    message
                )

                url = decision.get(
                    "url"
                )

            if not url:

                return {
                    "response":
                        "I couldn't determine the website.",
                    "action": None
                }

            action = TOOLS[
                "open_website"
            ].execute(
                url=url
            )

            return {
                "response":
                    f"Opening {url}...",
                "action": action
            }

        # SEARCH

        if intent == "web_search":

            query = decision.get(
                "query"
            )

            if not query:

                decision = self.fallback_intent(
                    message
                )

                query = decision.get(
                    "query"
                )

            if not query:

                return {
                    "response":
                        "I couldn't determine what to search.",
                    "action": None
                }

            action = TOOLS[
                "web_search"
            ].execute(
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

    # --------------------------------------------------
    # MAIN
    # --------------------------------------------------

    def think(self, message):

        message = message.strip()

        if not message:

            return {
                "response":
                    "I didn't receive a command.",
                "action": None
            }

        if not self.api_key:

            return {
                "response":
                    "AI configuration is missing.",
                "action": None
            }

        try:

            # ------------------------------------------
            # HARD ROUTING FOR SEARCH
            # ------------------------------------------

            search = self.detect_search(
                message
            )

            if search:

                return self.execute_intent(
                    {
                        "intent":
                            "web_search",
                        "query":
                            search
                    },
                    message
                )

            # ------------------------------------------
            # HARD ROUTING FOR WEBSITE
            # ------------------------------------------

            website = self.detect_website(
                message
            )

            if website:

                return self.execute_intent(
                    {
                        "intent":
                            "open_website",
                        "url":
                            website
                    },
                    message
                )

            # ------------------------------------------
            # AI
            # ------------------------------------------

            decision = self.ask_ai(
                message
            )

            return self.execute_intent(
                decision,
                message
            )

        except requests.HTTPError as e:

            status = e.response.status_code

            try:
                body = e.response.text
            except Exception:
                body = ""

            return {
                "response":
                    f"OpenRouter HTTP error {status}: "
                    f"{body[:500]}",
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

    def run(self, message):

        return self.think(message)