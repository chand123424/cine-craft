from fastapi import Request
from fastapi.responses import JSONResponse


class WorkflowError(Exception):
    def __init__(self, message: str, status_code: int = 409):
        self.message = message
        self.status_code = status_code


class AIProviderError(Exception):
    pass


async def workflow_error_handler(_: Request, exc: WorkflowError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


async def provider_error_handler(_: Request, exc: AIProviderError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": str(exc)})
