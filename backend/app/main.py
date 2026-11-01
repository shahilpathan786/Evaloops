from fastapi import FastAPI

app = FastAPI(
    title="EvalOps API",
    description="LLM Evaluation and Observability Platform",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to EvalOps",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "evalops-backend"
    }
