from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from API.v1.router import router as v1_router
from application.resolution.creation_locks import ResolutionLockTimeout
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title= "Ouranios Knowledgebase API",
    version= "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials= True,
    allow_methods = ["*"],
    allow_headers= ["*"]
)

app.include_router(
    v1_router,
    prefix= "/api/v1"
)


@app.exception_handler(ResolutionLockTimeout)
async def resolution_lock_timeout_handler(
    request: Request,
    exc: ResolutionLockTimeout,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": str(exc),
            "code": "resolution_lock_timeout",
        },
        headers={"Retry-After": "1"},
    )
