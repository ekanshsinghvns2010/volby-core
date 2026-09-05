import json
import os
import re
import requests

from .tools import TOOLS


class VolbyAgent:

    def __init__(self):

        self.name = "Volby Core"

        self.api_key = os.getenv(
            "OPENROUTER_API_KEY"
        )

        self.model = "openrouter/free"

        self.url = (
            "https://openrouter.ai/api/v1/chat/completions"
        )

    # ==================================================
    # DIRECT COMMAND DETECTION
    # ==================================================

    def detect_direct_command(self, message):

        text = message.strip()
        lower = text.lower()

        # ------------------------------------------------
        # OPEN WEBSITE
        # ------------------------------------------------

        website_match = re.search(
            r"(?:open|visit|go to)\s+"
            r"(https?://[^\s]+|"
            r"[a-zA-Z0-9-]+\."
            r"(?:com|org|net|in|io|co|dev)"
            r"(?:/[^\s]*)?)",
            text,
            re.IGNORECASE
        )

        if website_match:

            url = website_match.group(1)

            # Remove punctuation accidentally captured
            url = url.rstrip(
                ".,!?;:)"
            )

            if not url.startswith(
                ("http://", "https://")
            ):

                url = "https://" + url

            return {
                "intent": "open_website",
                "url": url
            }

        # ------------------------------------------------
        # SEARCH THE WEB
        # ------------------------------------------------

        search_prefixes = (

            "search the web for ",
            "search the internet for ",
            "search web for ",
            "search online for ",
            "search for ",
            "look up ",
            "find online "
        )

        for prefix in search_prefixes:

            if lower.startswith(prefix):

                query = text[
                    len(prefix):
                ].strip()

                if query:

                    return {
                        "intent": "web_search",
                        "query": query
                    }

        # ------------------------------------------------
        # EXPLICIT open_website COMMAND
        # ------------------------------------------------

        if lower.startswith(
            "open_website"
        ):

            value = re.sub(
                r"^open_website\s*",
                "",
                text,
                flags=re.IGNORECASE
            ).strip()

            if value:

                value = value.rstrip(
                    ".,!?;:)"
                )

                if not value.startswith(
                    ("http://", "https://")
                ):

                    value = "https://" + value

                return {
                    "intent": "open_website",
                    "url": value
                }

        # ------------------------------------------------
        # EXPLICIT web_search COMMAND
        # ------------------------------------------------

        if lower.startswith(
            "web_search"
        ):

            query = re.sub(
                r"^web_search\s*",
                "",
                text,
                flags=re.IGNORECASE
            ).strip()

            if query:

                return {
                    "intent": "web_search",
                    "query": query
                }

        # ------------------------------------------------
        # DEVICE STATUS
        # ------------------------------------------------

        if lower.startswith(
            "device_status"
        ):

            return {
                "intent": "device_status"
            }

        return None

# ==================================================
    # AI INTENT ROUTER
    # ==================================================

    def ask_ai(self, message):

        prompt = f"""
You are the intent router for Volby Core,
an Android AI agent.

Your job is to understand the user's command
and return the correct action.

Return ONLY valid JSON.

AVAILABLE INTENTS:

device_status
open_app
open_website
web_search
none

AVAILABLE APPS:

YouTube
WhatsApp
Instagram
Facebook
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

==================================================
IMPORTANT ROUTING RULES
==================================================

1. OPEN APPS

"Open YouTube"
-> {{"intent":"open_app","app":"YouTube"}}

"Watch videos"
-> {{"intent":"open_app","app":"YouTube"}}

"Open WhatsApp"
-> {{"intent":"open_app","app":"WhatsApp"}}

"Open Chrome"
-> {{"intent":"open_app","app":"Chrome"}}

"Open Instagram"
-> {{"intent":"open_app","app":"Instagram"}}


2. OPEN WEBSITES

If the user explicitly asks to open
a website or domain, ALWAYS use open_website.

"Open Wikipedia"
-> {{"intent":"open_website","url":"https://wikipedia.org"}}

"Open wikipedia.org"
-> {{"intent":"open_website","url":"https://wikipedia.org"}}

"Visit github.com"
-> {{"intent":"open_website","url":"https://github.com"}}

"Go to google.com"
-> {{"intent":"open_website","url":"https://google.com"}}

DO NOT use Chrome for these commands.


3. WEB SEARCH

If the user asks to search the web,
use web_search.

"Search the web for cricket news"
-> {{"intent":"web_search","query":"cricket news"}}

"Search for latest cricket schedule"
-> {{"intent":"web_search","query":"latest cricket schedule"}}

"Look up weather in Delhi"
-> {{"intent":"web_search","query":"weather in Delhi"}}

DO NOT use open_app Google or Chrome
for explicit web searches.


4. DEVICE STATUS

"Is my phone connected?"
-> {{"intent":"device_status"}}

"Check my device"
-> {{"intent":"device_status"}}


5. NORMAL CONVERSATION

"Hello"
-> {{"intent":"none"}}

"How are you?"
-> {{"intent":"none"}}


==================================================
STRICT RULES
==================================================

- Return ONLY JSON.
- Never return Markdown.
- Never explain the decision.
- Website/domain requests MUST use open_website.
- Explicit web searches MUST use web_search.
- App requests MUST use open_app.
- Device connection/status requests MUST use device_status.
- Normal conversation MUST use none.

USER REQUEST:

{message}
"""

        try:

            response = requests.post(

                self.url,

                headers={
                    "Authorization":
                        f"Bearer {self.api_key}",

                    "Content-Type":
                        "application/json",

                    "HTTP-Referer":
                        "https://github.com/"
                        "ekanshsinghvns2010/"
                        "volby-core",

                    "X-Title":
                        "Volby Core"
                },

                json={

                    "model":
                        self.model,

                    "messages": [

                        {
                            "role":
                                "system",

                            "content":
                                "Return only valid "
                                "JSON."
                        },

                        {
                            "role":
                                "user",

                            "content":
                                prompt
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

            # Remove accidental Markdown fences
            content = content.replace(
                "```json",
                ""
            )

            content = content.replace(
                "```",
                ""
            ).strip()

            try:

                return json.loads(
                    content
                )

            except json.JSONDecodeError:

                # Try to find JSON inside
                # additional model text

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

        except Exception:

            return None


    # ==================================================
    # FALLBACK ROUTER
    # ==================================================

    def fallback_intent(self, message):

        text = message.lower().strip()

        # ------------------------------------------------
        # WEBSITE
        # ------------------------------------------------

        website_match = re.search(

            r"(?:open|visit|go to)\s+"
            r"(https?://[^\s]+|"
            r"[a-zA-Z0-9-]+\."
            r"(?:com|org|net|in|io|co|dev)"
            r"(?:/[^\s]*)?)",

            message,

            re.IGNORECASE
        )

        if website_match:

            url = website_match.group(1)

            url = url.rstrip(
                ".,!?;:)"
            )

            if not url.startswith(
                ("http://", "https://")
            ):

                url = "https://" + url

            return {
                "intent":
                    "open_website",

                "url":
                    url
            }

        # ------------------------------------------------
        # WEB SEARCH
        # ------------------------------------------------

        search_prefixes = (

            "search the web for ",
            "search the internet for ",
            "search web for ",
            "search online for ",
            "search for ",
            "look up ",
            "find online "
        )

        for prefix in search_prefixes:

            if text.startswith(prefix):

                query = message[
                    len(prefix):
                ].strip()

                if query:

                    return {
                        "intent":
                            "web_search",

                        "query":
                            query
                    }

        # ------------------------------------------------
        # DEVICE STATUS
        # ------------------------------------------------

        device_phrases = (

            "check device",
            "device status",
            "phone status",
            "is my phone connected",
            "is my device connected",
            "is my phone online",
            "is my device online"
        )

        for phrase in device_phrases:

            if phrase in text:

                return {
                    "intent":
                        "device_status"
                }

        # ------------------------------------------------
        # APP DETECTION
        # ------------------------------------------------

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
            ],

            "Pinterest": [
                "pinterest"
            ],

            "Reddit": [
                "reddit"
            ],

            "Snapchat": [
                "snapchat"
            ],

            "Play Store": [
                "play store",
                "google play"
            ]

        }

        for app_name, phrases in app_patterns.items():

            for phrase in phrases:

                if phrase in text:

                    return {
                        "intent":
                            "open_app",

                        "app":
                            app_name
                    }

        # ------------------------------------------------
        # NOTHING MATCHED
        # ------------------------------------------------

        return {
            "intent":
                "none"
        }
# ==================================================
    # EXECUTE INTENT
    # ==================================================

    def execute_intent(self, decision, message):

        if not decision:
            decision = {
                "intent": "none"
            }

        intent = decision.get(
            "intent"
        )

        # ------------------------------------------------
        # DEVICE STATUS
        # ------------------------------------------------

        if intent == "device_status":

            try:

                tool = TOOLS[
                    "device_status"
                ]

                result = tool.execute()

                return {
                    "response":
                        f"Device status: {result}",

                    "action":
                        None
                }

            except Exception as e:

                return {
                    "response":
                        f"Could not check device status: {e}",

                    "action":
                        None
                }

        # ------------------------------------------------
        # OPEN APP
        # ------------------------------------------------

        if intent == "open_app":

            app_name = decision.get(
                "app"
            )

            if not app_name:

                return {
                    "response":
                        "I couldn't determine which app to open.",

                    "action":
                        None
                }

            try:

                tool = TOOLS[
                    "open_app"
                ]

                action = tool.execute(
                    app_name=app_name
                )

                return {
                    "response":
                        f"Opening {app_name}...",

                    "action":
                        action
                }

            except Exception as e:

                return {
                    "response":
                        f"Could not open {app_name}: {e}",

                    "action":
                        None
                }

        # ------------------------------------------------
        # OPEN WEBSITE
        # ------------------------------------------------

        if intent == "open_website":

            url = decision.get(
                "url"
            )

            if not url:

                return {
                    "response":
                        "I couldn't determine which website to open.",

                    "action":
                        None
                }

            try:

                tool = TOOLS[
                    "open_website"
                ]

                action = tool.execute(
                    url=url
                )

                return {
                    "response":
                        f"Opening {url}...",

                    "action":
                        action
                }

            except Exception as e:

                return {
                    "response":
                        f"Could not open website: {e}",

                    "action":
                        None
                }

        # ------------------------------------------------
        # WEB SEARCH
        # ------------------------------------------------

        if intent == "web_search":

            query = decision.get(
                "query"
            )

            if not query:

                return {
                    "response":
                        "I couldn't determine what to search for.",

                    "action":
                        None
                }

            try:

                tool = TOOLS[
                    "web_search"
                ]

                action = tool.execute(
                    query=query
                )

                return {
                    "response":
                        f"Searching the web for {query}...",

                    "action":
                        action
                }

            except Exception as e:

                return {
                    "response":
                        f"Could not perform web search: {e}",

                    "action":
                        None
                }

        # ------------------------------------------------
        # NORMAL CONVERSATION
        # ------------------------------------------------

        return {
            "response":
                f"I received your command: {message}",

            "action":
                None
        }


    # ==================================================
    # MAIN THINK FUNCTION
    # ==================================================

    def think(self, message: str):

        message = message.strip()

        if not message:

            return {
                "response":
                    "I didn't receive a command.",

                "action":
                    None
            }

        # ------------------------------------------------
        # DIRECT COMMANDS FIRST
        # ------------------------------------------------

        direct = self.detect_direct_command(
            message
        )

        if direct:

            return self.execute_intent(
                direct,
                message
            )

        # ------------------------------------------------
        # AI ROUTING
        # ------------------------------------------------

        if self.api_key:

            decision = self.ask_ai(
                message
            )

            if decision:

                return self.execute_intent(
                    decision,
                    message
                )

        # ------------------------------------------------
        # LOCAL FALLBACK
        # ------------------------------------------------

        fallback = self.fallback_intent(
            message
        )

        return self.execute_intent(
            fallback,
            message
        )


    # ==================================================
    # RUN
    # ==================================================

    def run(self, message: str):

        return self.think(
            message
        )