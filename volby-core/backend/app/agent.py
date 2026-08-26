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
    # WEBSITE DETECTION
    # ==================================================

    def detect_website(self, message):

        text = message.strip()

        patterns = [

            # https://wikipedia.org
            r"(https?://[^\s]+)",

            # wikipedia.org
            r"\b([a-zA-Z0-9-]+\."
            r"(?:com|org|net|in|io|co|dev)"
            r"(?:/[^\s]*)?)\b"

        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                url = match.group(1)

                if not url.startswith(
                    ("http://", "https://")
                ):
                    url = "https://" + url

                return url

        return None

    # ==================================================
    # SEARCH DETECTION
    # ==================================================

    def detect_search(self, message):

        text = message.strip()

        prefixes = [

            "search the web for ",
            "search the internet for ",
            "search for ",
            "search web for ",
            "look up "

        ]

        for prefix in prefixes:

            if text.lower().startswith(prefix):

                query = text[
                    len(prefix):
                ].strip()

                if query:
                    return query

        return None

    # ==================================================
    # EXPLICIT TOOL COMMANDS
    # ==================================================

    def detect_explicit_tool(self, message):

        text = message.lower().strip()

        # ----------------------------------------------
        # OPEN WEBSITE
        # ----------------------------------------------

        if "open_website" in text:

            # First look for an actual URL/domain
            url = self.detect_website(message)

            if url:

                return {
                    "intent": "open_website",
                    "url": url
                }

            # Example:
            # call open_website to open Wikipedia

            match = re.search(
                r"(?:open|visit|go to)\s+"
                r"([a-zA-Z0-9-]+)",
                message,
                re.IGNORECASE
            )

            if match:

                site = match.group(1).strip()

                return {
                    "intent": "open_website",
                    "url": "https://" + site + ".com"
                }

        # ----------------------------------------------
        # WEB SEARCH
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
        # DEVICE STATUS
        # ----------------------------------------------

        if "device_status" in text:

            return {
                "intent": "device_status"
            }

        return None

    # ==================================================
    # FALLBACK INTENT
    # ==================================================

    def fallback_intent(self, message):

        text = message.lower().strip()

        # Website first

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
            "check my phone",
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
                "watch some videos",
                "watch video"
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
                "browse the web",
                "browse the internet"
            ],

            "Google": [
                "google"
            ],

            "Gmail": [
                "gmail",
                "check my email",
                "check my emails"
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
You are Volby Core's intent router.

Understand the user's natural-language request.

Available intents:

device_status
open_app
open_website
web_search
none

Rules:

1. If the user wants an Android application,
use open_app.

2. If the user wants a website,
use open_website.

3. If the user wants to search for information,
use web_search.

4. If the user asks about device connection/status,
use device_status.

5. Otherwise use none.

Examples:

"I want to watch some videos"

{{"intent":"open_app","app":"YouTube"}}

"I need to message my friend"

{{"intent":"open_app","app":"WhatsApp"}}

"Open Chrome"

{{"intent":"open_app","app":"Chrome"}}

"Open wikipedia.org"

{{"intent":"open_website","url":"https://wikipedia.org"}}

"Go to wikipedia.org"

{{"intent":"open_website","url":"https://wikipedia.org"}}

"Search the web for the latest cricket schedule"

{{"intent":"web_search","query":"latest cricket schedule"}}

"Is my phone connected?"

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
    # EXECUTE INTENT
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

        # ----------------------------------------------
        # DEVICE STATUS
        # ----------------------------------------------

        if intent == "device_status":

            result = TOOLS[
                "device_status"
            ].execute()

            return {
                "response":
                    f"Device status: {result}",
                "action": None
            }

        # ----------------------------------------------
        # OPEN APP
        # ----------------------------------------------

        if intent == "open_app":

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

        # ----------------------------------------------
        # OPEN WEBSITE
        # ----------------------------------------------

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

        # ----------------------------------------------
        # WEB SEARCH
        # ----------------------------------------------

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

        # ----------------------------------------------
        # NONE
        # ----------------------------------------------

        return {
            "response":
                f"I received your command: {message}",
            "action": None
        }

    # ==================================================
    # MAIN THINKING LOOP
    # ==================================================

    def think(self, message):

        # DIAGNOSTIC MARKER
        print(
            "========================================"
        )

        print(
            "VOLBY NEW AGENT VERSION 2026-08-26"
        )

        print(
            "Incoming message:",
            message
        )

        print(
            "========================================"
        )

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
            # 1. EXPLICIT TOOL COMMAND
            # ------------------------------------------

            explicit = self.detect_explicit_tool(
                message
            )

            if explicit:

                print(
                    "ROUTER: explicit tool"
                )

                print(
                    "DECISION:",
                    explicit
                )

                return self.execute_intent(
                    explicit,
                    message
                )

            # ------------------------------------------
            # 2. WEBSITE
            # ------------------------------------------

            website = self.detect_website(
                message
            )

            if website:

                decision = {
                    "intent":
                        "open_website",
                    "url":
                        website
                }

                print(
                    "ROUTER: website"
                )

                print(
                    "DECISION:",
                    decision
                )

                return self.execute_intent(
                    decision,
                    message
                )

            # ------------------------------------------
            # 3. SEARCH
            # ------------------------------------------

            search = self.detect_search(
                message
            )

            if search:

                decision = {
                    "intent":
                        "web_search",
                    "query":
                        search
                }

                print(
                    "ROUTER: search"
                )

                print(
                    "DECISION:",
                    decision
                )

                return self.execute_intent(
                    decision,
                    message
                )

            # ------------------------------------------
            # 4. AI
            # ------------------------------------------

            print(
                "ROUTER: AI"
            )

            decision = self.ask_ai(
                message
            )

            print(
                "AI DECISION:",
                decision
            )

            # ------------------------------------------
            # 5. FALLBACK
            # ------------------------------------------

            if not decision:

                print(
                    "AI failed; using fallback."
                )

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