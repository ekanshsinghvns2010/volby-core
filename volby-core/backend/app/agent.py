import json

from .llm import LLM
from .tools import TOOLS


class VolbyAgent:
    def __init__(self):
        self.name = "Volby Core"
        self.llm = LLM()

    def get_tool_schemas(self):
        return [tool.schema() for tool in TOOLS.values()]

    def run(self, message: str) -> str:
        message = message.strip()

        if not message:
            return "I didn't receive a command."

        messages = [
            {
                "role": "system",
                "content": (
                    "You are Volby Core, a personal AI agent. "
                    "Use tools when they are useful. "
                    "Never claim an action happened unless a tool "
                    "actually performed it."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ]

        for _ in range(5):
            response = self.llm.client.chat.completions.create(
                model=self.llm.model,
                messages=messages,
                tools=self.get_tool_schemas(),
            )

            assistant_message = response.choices[0].message

            messages.append(assistant_message)

            if not assistant_message.tool_calls:
                return assistant_message.content or ""

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name

                if tool_name not in TOOLS:
                    continue

                tool = TOOLS[tool_name]

                try:
                    arguments = json.loads(
                        tool_call.function.arguments or "{}"
                    )
                except json.JSONDecodeError:
                    arguments = {}

                result = tool.execute(**arguments)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )

        return "I couldn't complete the request."