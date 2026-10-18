## 1. Project Setup

- [x] 1.1 Create `chatbot/` directory structure with `app/`, `app/services/`, `app/tools/` subdirectories and `__init__.py` files
- [x] 1.2 Create `requirements.txt` with dependencies: `fastapi`, `uvicorn`, `langchain`, `langchain-openai`, `httpx`, `pyjwt`, `pydantic-settings`, `python-dotenv`
- [x] 1.3 Create `.env.example` with required environment variables: `JWT_SECRET`, `LLM_API_KEY`, `LLM_MODEL`, `UPSTREAM_API_URL`
- [x] 1.4 Create `app/config.py` with Pydantic Settings class that loads environment variables and fails fast if `JWT_SECRET` is not set

## 2. Authentication

- [x] 2.1 Create `app/auth.py` with JWT validation function that checks signature and expiration using `PyJWT` and the configured `JWT_SECRET`
- [x] 2.2 Create a FastAPI dependency (`get_current_token`) that extracts the `Authorization: Bearer <token>` header, validates the JWT, and returns the raw token for forwarding
- [x] 2.3 Return HTTP 401 with `{ "error": "unauthorized", "message": "Invalid or expired JWT token" }` for missing, expired, or malformed tokens

## 3. Upstream API Client

- [x] 3.1 Create `app/services/upstream.py` with an async `httpx.AsyncClient` wrapper for the upstream Air Project API
- [x] 3.2 Implement `get_current_air_quality(token, device_id=None)` method calling `GET /api/air-quality/current`
- [x] 3.3 Implement `get_historical_air_quality(token, range=None, from_date=None, to_date=None, device_id=None)` method calling `GET /api/air-quality/historical`
- [x] 3.4 Implement `get_user_preferences(token)` method calling `GET /api/preferences/me`
- [x] 3.5 Implement `get_user_profile(token)` method calling `GET /api/users/me`
- [x] 3.6 Add error handling: return clear errors when upstream is unreachable (for 502 responses)

## 4. LangChain Tools

- [x] 4.1 Create `app/tools/air_quality.py` with a `get_current_air_quality` LangChain tool that wraps the upstream current readings endpoint
- [x] 4.2 Create a `get_historical_air_quality` LangChain tool that wraps the upstream historical data endpoint with parameters for range, from/to dates, and deviceId
- [x] 4.3 Ensure all tools forward the user's JWT token in upstream requests and only perform GET operations

## 5. Chat Service (LangChain Agent)

- [x] 5.1 Create `app/services/chat.py` with the LangChain agent setup using `AgentExecutor`, system prompt, and the air quality tools
- [x] 5.2 Build the system prompt instructing the LLM to: greet the user by their first name, only use data from tool responses, never fabricate values, and respond in the user's detected language
- [x] 5.3 Implement `process_chat_message(message, token, language)` function that runs the agent and returns the reply

## 6. Request/Response Schemas

- [x] 6.1 Create `app/schemas.py` with Pydantic models: `ChatRequest` (message: str, 1-1000 chars), `ChatResponse` (reply: str, language: ES|EN), `ErrorResponse` (error: str, message: str), `HealthResponse` (status: str, version: str)

## 7. FastAPI Application & Routes

- [x] 7.1 Create `app/main.py` with FastAPI app instance and CORS middleware configuration
- [x] 7.2 Implement `POST /api/chat` route: validate JWT → fetch user profile (`firstName`) and language preference (default EN on failure) → run LangChain agent → return ChatResponse
- [x] 7.3 Implement `GET /health` route returning `{ "status": "ok", "version": "1.0.0" }` without authentication
- [x] 7.4 Add exception handlers for 401, 422, 502, and 500 error responses matching the OpenAPI spec

## 8. Documentation & Configuration

- [x] 8.1 Create `chatbot/README.md` with setup instructions, environment variable documentation, and usage examples
