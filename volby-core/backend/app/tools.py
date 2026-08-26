class Tool:
    def __init__(self, name, description, function, parameters=None):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters or {
            "type": "object",
            "properties": {},
            "required": [],
        }

    def execute(self, **kwargs):
        return self.function(**kwargs)

    def schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


def get_device_status():
    return {
        "status": "connected",
        "platform": "android",
        "access": "limited",
    }


TOOLS = {
    "device_status": Tool(
        name="device_status",
        description="Check whether the Android device is connected.",
        function=get_device_status,
    )
}