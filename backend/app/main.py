from fastapi import FastAPI

app = FastAPI(title="RAG Eval")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
