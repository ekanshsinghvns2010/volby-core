from app.llm import LLM


llm = LLM()

response = llm.generate(
    "You are Volby Core. Reply with exactly: Volby Core online."
)

print(response)