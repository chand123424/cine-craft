from fastapi import FastAPI

from app.exceptions import AIProviderError, WorkflowError, provider_error_handler, workflow_error_handler
from app.routes import scenes, scripts

app = FastAPI(title="CineCraft AI Engine", version="0.1.0")
app.include_router(scripts.router, prefix="/api")
app.include_router(scenes.router, prefix="/api")
app.add_exception_handler(WorkflowError, workflow_error_handler)
app.add_exception_handler(AIProviderError, provider_error_handler)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
