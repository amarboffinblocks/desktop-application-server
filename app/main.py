import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api_router import api_router
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import HTTPException
from app.core.config import Settings
settings = Settings()

app = FastAPI(title="YourUniverse.ai API")

# Allow CORS for desktop app (localhost, 127.0.0.1, file:// for Electron)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "file://"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "YourUniverse.ai backend is running!"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "detail": exc.detail},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "Internal server error."},
    )

