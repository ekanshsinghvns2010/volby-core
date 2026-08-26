class Tool:
    def __init__(self, name, description, function):
        self.name = name
        self.description = description
        self.function = function

    def execute(self, **kwargs):
        return self.function(**kwargs)


def get_device_status():
    return {
        "status": "connected",
        "platform": "android",
        "access": "limited"
    }


TOOLS = {
    "device_status": Tool(
        name="device_status",
        description="Check whether the Android device is connected.",
        function=get_device_status
    )
}