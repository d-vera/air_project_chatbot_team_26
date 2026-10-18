import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import SecurityBase
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer

from app.auth import UnauthorizedException, get_current_token
from app.config import get_settings
from app.schemas import ChatRequest, ChatResponse, ErrorResponse, HealthResponse, LanguageEnum
from app.services.chat import process_chat_message
from app.services.upstream import BadGatewayException, UpstreamClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate startup configuration (e.g. JWT_SECRET)
    get_settings()
    yield


bearer_scheme = HTTPBearer()

app = FastAPI(
    title="Air Quality Chatbot API",
    description="LangChain-powered chatbot backend for environmental measurements in the Air Project.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extract message from first error if available
    errors = exc.errors()
    msg = "Message must not be empty or exceed length limits"
    if errors:
        msg = errors[0].get("msg", msg)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "unprocessable_entity", "message": msg},
    )


@app.exception_handler(UnauthorizedException)
async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {"error": "unauthorized", "message": str(exc.detail)},
    )


@app.exception_handler(BadGatewayException)
async def bad_gateway_exception_handler(request: Request, exc: BadGatewayException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {"error": "bad_gateway", "message": str(exc.detail)},
    )


@app.exception_handler(HTTPException)
async def generic_http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail and "message" in exc.detail:
        content = exc.detail
    else:
        err_code = "error"
        if exc.status_code == 401:
            err_code = "unauthorized"
        elif exc.status_code == 422:
            err_code = "unprocessable_entity"
        elif exc.status_code == 502:
            err_code = "bad_gateway"
        elif exc.status_code == 500:
            err_code = "internal_error"
        content = {"error": err_code, "message": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content=content)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred while processing your request",
        },
    )


@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
)
async def health():
    return HealthResponse(status="ok", version="1.0.0")


@app.post(
    "/api/chat",
    response_model=ChatResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        422: {"model": ErrorResponse, "description": "Unprocessable Entity"},
        502: {"model": ErrorResponse, "description": "Bad Gateway"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    tags=["Chat"],
    summary="Send a chat message",
)
async def chat(
    payload: ChatRequest,
    token: str = Depends(get_current_token),
    _credentials=Depends(bearer_scheme),
):
    upstream_client = UpstreamClient()

    # Fetch preferences and user profile concurrently (failures fallback gracefully)
    pref_task = upstream_client.get_user_preferences(token)
    profile_task = upstream_client.get_user_profile(token)
    preferences, profile = await asyncio.gather(pref_task, profile_task)

    # Resolve language preference
    lang = LanguageEnum.EN
    if preferences and isinstance(preferences, dict):
        raw_lang = preferences.get("language")
        if raw_lang and str(raw_lang).upper() == "ES":
            lang = LanguageEnum.ES

    # Resolve first name for personalized greeting
    first_name = None
    if profile and isinstance(profile, dict):
        first_name = profile.get("firstName")

    reply = await process_chat_message(
        message=payload.message,
        token=token,
        language=lang.value,
        first_name=first_name,
        upstream_client=upstream_client,
    )

    return ChatResponse(reply=reply, language=lang)
