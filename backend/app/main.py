from fastapi import FastAPI
from .agent import VolbyAgent

app = FastAPI(
    title="Volby Core",
    description="Personal AI Agent Core",
    version="0.1.0"
)

agent = VolbyAgent()


@app.get("/")
def root():
    return {
        "name": "Volby Core",
        "status": "online",
        "version": "0.1.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/chat")
def chat(message: str):
    response = agent.run(message)

    return {
        "message": message,
        "response": response
    }