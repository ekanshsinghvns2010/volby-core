from fastapi import FastAPI

app = FastAPI(
    title="Volby Core",
    description="Personal AI Agent Core",
    version="0.1.0"
)


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
    return {
        "message": message,
        "response": "Volby Core received your message."
    }