from fastapi import FastAPI
from app.api.projects import router as projects_router
from app.api.auth import router as auth_router
from app.api.datasets import router as datasets_router




app = FastAPI(
    title="EvalOps API",
    description="LLM Evaluation and Observability Platform",
    version="0.1.0"
)

app.include_router(
    projects_router,
    prefix="/api/v1"
)

app.include_router(auth_router, prefix="/api/v1")

app.include_router(datasets_router , prefix="/api/v1")


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
