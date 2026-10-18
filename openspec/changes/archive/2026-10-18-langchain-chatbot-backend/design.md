## Context

The Air Project has a Spring Boot backend (port `8080`) managing sensors and air quality data, secured with JWT. There is no conversational interface — users rely on dashboards or raw API calls. This design introduces a separate Python service (port `8000`) that wraps the read-only air quality endpoints with an LLM-powered chatbot using LangChain.

The existing `openapi-chatbot.yaml` in the repo root defines the API contract for this new service.

## Goals / Non-Goals

**Goals:**
- Provide a single `POST /api/chat` endpoint for natural-language air quality queries
- Validate JWTs locally and forward them to the upstream API for data access
- Respond in the user's preferred language (ES/EN) by reading their preferences
- Use LangChain agent with tools to decide which upstream endpoints to call
- Keep the service stateless — no database, no session storage

**Non-Goals:**
- No conversation history / multi-turn memory (each request is independent)
- No writing, updating, or deleting data in the upstream API
- No sensor management — only air quality data endpoints are consumed
- No user registration or authentication flows — JWT is obtained externally
- No WebSocket/STOMP real-time features in this service
- No fine-tuning or custom model training

## Decisions

### 1. Framework: FastAPI over Flask/Django

**Choice**: FastAPI with Uvicorn

**Rationale**: FastAPI provides async support out of the box (critical for non-blocking upstream HTTP calls), automatic OpenAPI doc generation, and Pydantic models for request/response validation. Flask would require additional libraries for async; Django is overkill for a single-endpoint service.

**Alternatives considered**: Flask + gunicorn (simpler but no native async), Django REST Framework (too heavy).

### 2. LangChain Agent with Tools Pattern

**Choice**: LangChain `AgentExecutor` with custom tools for each upstream endpoint.

**Rationale**: The agent pattern lets the LLM decide *which* upstream endpoints to call based on the user's question, rather than hardcoding routing logic. Two tools will be defined:

| Tool | Wraps | Purpose |
|------|-------|---------|
| `get_current_air_quality` | `GET /api/air-quality/current` | Latest readings, optional deviceId filter |
| `get_historical_air_quality` | `GET /api/air-quality/historical` | Time-series data with range or custom dates |

**Alternatives considered**: Simple chain with manual intent classification (brittle, hard to extend), RAG over stored data (unnecessary — data is live via API).

### 3. HTTP Client: httpx (async)

**Choice**: `httpx.AsyncClient` for all upstream calls.

**Rationale**: Native async support aligns with FastAPI's async handlers. Connection pooling via a shared client instance. `requests` library is synchronous and would block the event loop.

### 4. JWT Handling: Validate Locally + Forward

**Choice**: Validate the JWT signature and expiry using `PyJWT` with the same secret/public key as the upstream API. Then forward the raw token in `Authorization: Bearer <token>` headers to upstream calls.

**Rationale**: Local validation lets the chatbot reject expired/invalid tokens early (fast 401) without hitting the upstream API. Forwarding the original token ensures the upstream API applies its own authorization rules (e.g., visitors can't access LAST_YEAR range).

**Configuration**: The JWT secret/key will be provided via an environment variable (`JWT_SECRET`).

### 5. Project Structure

```
chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, routes, startup
│   ├── config.py             # Environment config (Pydantic Settings)
│   ├── auth.py               # JWT validation logic
│   ├── schemas.py            # Request/Response Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── upstream.py       # httpx client for Air Project API
│   │   └── chat.py           # LangChain agent setup and execution
│   └── tools/
│       ├── __init__.py
│       └── air_quality.py    # LangChain tools wrapping upstream endpoints
├── requirements.txt
├── .env.example
└── README.md
```

### 6. LLM Provider Configuration

**Choice**: Configurable via environment variable (`LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`). Default to OpenAI (`gpt-4o-mini`) but support swapping.

**Rationale**: Avoids vendor lock-in. The LangChain abstraction makes provider-swapping straightforward.

### 7. Language-Aware & Personalized Prompting

**Choice**: Fetch user preferences and profile on each request, inject language and user name into the system prompt.

**Flow**:
1. On `POST /api/chat`, call `GET /api/preferences/me` and `GET /api/users/me` with the forwarded JWT
2. Extract `language` field (`ES` or `EN`) from preferences
3. Extract `firstName` from the user profile
4. Include in the LangChain system prompt: _"Greet the user by their name: {firstName}. Respond in {language}."_
5. Return the detected language in the response body

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| **Upstream API downtime** → chatbot returns 502 | Wrap upstream calls in try/catch, return clear `502 Bad Gateway` error |
| **LLM latency** → slow responses (2-5s typical) | Use streaming in the future if needed; for v1, synchronous response is acceptable |
| **LLM hallucination** → incorrect air quality data | System prompt instructs the LLM to only use data from tool responses, never fabricate values |
| **JWT secret mismatch** → all tokens rejected | Document JWT_SECRET configuration clearly; fail-fast on startup if not set |
| **Token cost** → high API usage | Use `gpt-4o-mini` as default (cost-effective); set max_tokens limit on responses |
| **No conversation memory** → context lost between messages | Acceptable for v1; each question is self-contained |
