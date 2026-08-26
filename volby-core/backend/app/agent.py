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
    # FALLBACK INTENT DETECTION
    # --------------------------------------------------

    def fallback_intent(self, message):

        text = message.lower().strip()

        # -----------------------------
        # DEVICE STATUS
        # -----------------------------

        device_phrases = [
            "is my phone connected",
            "is my device connected",
            "check my device",
            "check device",
            "device status",
            "phone status",
            "is the phone connected"
        ]

        for phrase in device_phrases:
            if phrase in text:
                return {
                    "intent": "device_status"
                }

        # -----------------------------
        # SEARCH
        # -----------------------------

        search_prefixes = [
            "search the web for ",
            "search for ",
            "search the internet for ",
            "google ",
            "look up "
        ]

        for prefix in search_prefixes:

            if text.startswith(prefix):

                query = message[len(prefix):].strip()

                if query:
                    return {
                        "intent": "web_search",
                        "query": query
                    }

        # -----------------------------
        # WEBSITE
        # -----------------------------

        website_match = re.search(
            r"(?:open|visit|go to)\s+"
            r"(https?://[^\s]+|"
            r"[a-zA-Z0-9-]+\.(?:com|org|net|in|io)[^\s]*)",
            text
        )

        if website_match:

            url = website_match.group(1)

            if not url.startswith("http"):
                url = "https://" + url

            return {
                "intent": "open_website",
                "url": url
            }

        # -----------------------------
        # APP KEYWORDS
        # -----------------------------

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
                "google",
                "search something"
            ],

            "gmail": [
                "gmail",
                "check my email",
                "check my emails",
                "read my email"
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
                "netflix",
                "watch a movie"
            ]
        }

        for app_name, phrases in apps.items():

            for phrase in phrases:

                if phrase in text:

                    display_name = app_name.title()

                    if app_name == "youtube":
                        display_name = "YouTube"

                    elif app_name == "whatsapp":
                        display_name = "WhatsApp"

                    elif app_name == "instagram":
                        display_name = "Instagram"

                    elif app_name == "facebook":
                        display_name = "Facebook"

                    elif app_name == "chrome":
                        display_name = "Chrome"

                    elif app_name == "google":
                        display_name = "Google"

                    elif app_name == "gmail":
                        display_name = "Gmail"

                    elif app_name == "linkedin":
                        display_name = "LinkedIn"

                    elif app_name == "spotify":
                        display_name = "Spotify"

                    elif app_name == "telegram":
                        display_name = "Telegram"

                    elif app_name == "discord":
                        display_name = "Discord"

                    elif app_name == "netflix":
                        display_name = "Netflix"

                    return {
                        "intent": "open_app",
                        "app": display_name
                    }

        return {
            "intent": "none"
        }

    # --------------------------------------------------
    # AI REQUEST
    # --------------------------------------------------

    def ask_ai(self, message):

        prompt = f"""
You are Volby Core's intent router.

Understand the user's request and return ONE JSON object.

Available intents:

device_status
open_app
open_website
web_search
none

For open_app include:
"app"

For open_website include:
"url"

For web_search include:
"query"

Examples:

User:
I want to watch some videos

JSON:
{{"intent":"open_app","app":"YouTube"}}

User:
I need to message my friend

JSON:
{{"intent":"open_app","app":"WhatsApp"}}

User:
Search the web for the latest cricket schedule

JSON:
{{"intent":"web_search","query":"latest cricket schedule"}}

User:
Open wikipedia.org

JSON:
{{"intent":"open_website","url":"https://wikipedia.org"}}

User:
Is my phone connected?

JSON:
{{"intent":"device_status"}}

User:
Hello

JSON:
{{"intent":"none"}}

Return ONLY JSON.

User request:
{message}
"""

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

        choices = data.get("choices", [])

        if not choices:
            return None

        content = (
            choices[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        # Remove markdown fences if model adds them.

        content = content.replace(
            "```json",
            ""
        )

        content = content.replace(
            "```",
            ""
        )

        content = content.strip()

        # Try normal JSON.

        try:
            return json.loads(content)

        except json.JSONDecodeError:
            pass

        # Try extracting JSON from surrounding text.

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
    # TOOL EXECUTION
    # --------------------------------------------------

    def execute_intent(self, decision, message):

        if not decision:
            decision = self.fallback_intent(
                message
            )

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
                decision = self.fallback_intent(
                    message
                )

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
                decision = self.fallback_intent(
                    message
                )

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
                decision = self.fallback_intent(
                    message
                )

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

        # NOTHING
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