class Tool:
    def __init__(self, name, description, function):
        self.name = name
        self.description = description
        self.function = function

    def execute(self, **kwargs):
        return self.function(**kwargs)


# -------------------------
# DEVICE STATUS
# -------------------------

def get_device_status():
    return {
        "status": "connected",
        "platform": "android",
        "access": "limited"
    }


# -------------------------
# OPEN APP
# -------------------------

def prepare_open_app(app_name: str):
    return {
        "action": "open_app",
        "app": app_name
    }


# -------------------------
# OPEN WEBSITE
# -------------------------

def prepare_open_website(url: str):
    return {
        "action": "open_website",
        "url": url
    }


# -------------------------
# WEB SEARCH
# -------------------------

def prepare_web_search(query: str):
    return {
        "action": "web_search",
        "query": query
    }


# -------------------------
# TOOL REGISTRY
# -------------------------

TOOLS = {

    "device_status": Tool(
        name="device_status",
        description="Check the connection status of the Android device.",
        function=get_device_status
    ),

    "open_app": Tool(
        name="open_app",
        description="Open an installed Android application.",
        function=prepare_open_app
    ),

    "open_website": Tool(
        name="open_website",
        description="Open a website on the Android device.",
        function=prepare_open_website
    ),

    "web_search": Tool(
        name="web_search",
        description="Search the web for information.",
        function=prepare_web_search
    )
}