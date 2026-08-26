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

        self.url = (
            "https://openrouter.ai/api/v1/chat/completions"
        )

    # ==================================================
    # EXPLICIT TOOL COMMANDS
    # ==================================================

    def detect_explicit_tool(self, message):

        text = message.lower().strip()

        # ----------------------------------------------
        # open_website
        # ----------------------------------------------

        if "open_website" in text:

            match = re.search(
                r"(?:open_website).*?"
                r"(?:open|visit|go to)?\s*"
                r"(https?://[^\s]+|"
                r"[a-zA-Z0-9-]+\.(?:com|org|net|in|io)"
                r"(?:/[^\s]*)?)",
                message,
                re.IGNORECASE
            )

            if match:

                url = match.group(1)

                if not url.startswith("http://") and \
                   not url.startswith("https://"):

                    url = "https://" + url

                return {
                    "intent": "open_website",
                    "url": url
                }

        # ----------------------------------------------
        # web_search
        # ----------------------------------------------

        if "web_search" in text:

            query = re.sub(
                r".*?web_search",
                "",
                message,
                flags=re.IGNORECASE
            )

            query = re.sub(
                r"^(?:to|for|about|search)\s+",
                "",
                query,
                flags=re.IGNORECASE
            ).strip()

            if query:

                return {
                    "intent": "web_search",
                    "query": query
                }

        # ----------------------------------------------
        # device_status
        # ----------------------------------------------

        if "device_status" in text:

            return {
                "intent": "device_status"
            }

        # ----------------------------------------------
        # open_app
        # ----------------------------------------------

        if "open_app" in text:

            match = re.search(
                r"open_app.*?"
                r"(?:open|launch|start)?\s*"
                r"([A-Za-z][A-Za-z0-9 ]*)$",
                message,
                re.IGNORECASE
            )

            if match:

                return {
                    "intent": "open_app",
                    "app": match.group(1).strip()
                }

        return None

    # ==================================================
    # WEBSITE DETECTION
    # ==================================================

    def detect_website(self, message):

        patterns = [

            r"(?:open|visit|go to)\s+"
            r"(https?://[^\s]+)",

            r"(?:open|visit|go to)\s+"
            r"([a-zA-Z0-9-]+\.(?:com|org|net|in|io)"
            r"(?:/[^\s]*)?)"

        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                message,
                re.IGNORECASE
            )

            if match:

                url = match.group(1)

                if not url.startswith("http://") and \
                   not url.startswith("https://"):

                    url = "https://" + url

                return url

        return None

    # ==================================================
    # SEARCH DETECTION
    # ==================================================

    def detect_search(self, message):

        prefixes = [

            "search the web for ",
            "search the internet for ",
            "search for ",
            "look up "

        ]

        for prefix in prefixes:

            if message.lower().startswith(prefix):

                query = message[
                    len(prefix):
                ].strip()

                if query:

                    return query

        return None

    # ==================================================
    # FALLBACK
    # ==================================================

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

            "check device",
            "device status",
            "phone status",
            "is my phone connected",
            "is my device connected"

        ]

        for phrase in device_phrases:

            if phrase in text:

                return {
                    "intent": "device_status"
                }

        # Apps

        app_patterns = {

            "YouTube": [
                "youtube",
                "watch videos",
                "watch a video",
                "watch some videos"
            ],

            "WhatsApp": [
                "whatsapp",
                "message my friend",
                "message someone",
                "send a message",
                "chat with my friend"
            ],

            "Instagram": [
                "instagram",
                "look at reels"
            ],

            "Facebook": [
                "facebook"
            ],

            "Chrome": [
                "chrome",
                "browse the web"
            ],

            "Google": [
                "google"
            ],

            "Gmail": [
                "gmail",
                "check my email"
            ],

            "LinkedIn": [
                "linkedin"
            ],

            "Spotify": [
                "spotify",
                "listen to music"
            ],

            "Telegram": [
                "telegram"
            ],

            "Discord": [
                "discord"
            ],

            "Netflix": [
                "netflix"
            ]

        }

        for app_name, phrases in app_patterns.items():

            for phrase in phrases:

                if phrase in text:

                    return {
                        "intent": "open_app",
                        "app": app_name
                    }

        return {
            "intent": "none"
        }

    # ==================================================
    # AI CLASSIFIER
    # ==================================================

    def ask_ai(self, message):

        prompt = f"""
You are the intent router for Volby Core.

Available intents:

device_status
open_app
open_website
web_search
none

Return ONLY JSON.

Examples:

I want to watch videos
{{"intent":"open_app","app":"YouTube"}}

I need to message my friend
{{"intent":"open_app","app":"WhatsApp"}}

Open Chrome
{{"intent":"open_app","app":"Chrome"}}

Open wikipedia.org
{{"intent":"open_website","url":"https://wikipedia.org"}}

Search the web for cricket schedule
{{"intent":"web_search","query":"cricket schedule"}}

Is my phone connected?
{{"intent":"device_status"}}

User:
{message}
"""

        response = requests.post(

            self.url,

            headers={
                "Authorization":
                    f"Bearer {self.api_key}",

                "Content-Type":
                    "application/json"
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
        ).strip()

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

                    return None

        return None

    # ==================================================
    # EXECUTE
    # ==================================================

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

            app = decision.get(
                "app"
            )

            if not app:

                decision = self.fallback_intent(
                    message
                )

                app = decision.get(
                    "app"
                )

            if not app:

                return {
                    "response":
                        "I couldn't determine which app to open.",
                    "action": None
                }

            action = TOOLS[
                "open_app"
            ].execute(
                app_name=app
            )

            return {
                "response":
                    f"Opening {app}...",
                "action": action
            }

        # WEBSITE

        if intent == "open_website":

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

        return {
            "response":
                f"I received your command: {message}",
            "action": None
        }

    # ==================================================
    # MAIN
    # ==================================================

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

            # 1. Explicit tool commands

            explicit = self.detect_explicit_tool(
                message
            )

            if explicit:

                return self.execute_intent(
                    explicit,
                    message
                )

            # 2. Website

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

            # 3. Search

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

            # 4. AI

            decision = self.ask_ai(
                message
            )

            # 5. If AI fails, fallback

            if not decision:

                decision = self.fallback_intent(
                    message
                )

            return self.execute_intent(
                decision,
                message
            )

        except requests.HTTPError as e:

            status = e.response.status_code

            body = ""

            try:
                body = e.response.text
            except Exception:
                pass

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