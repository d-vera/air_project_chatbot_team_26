## Why

The Air Project ecosystem has a rich REST API with air quality measurements (temperature, humidity, CO₂, PM1.0, PM2.5, PM10) but no conversational interface. Users must navigate API endpoints directly or use a dashboard. A chatbot allows anyone — including non-technical users — to ask natural-language questions about environmental data and receive answers in their preferred language (Spanish or English).

## What Changes

- **New Python backend** using FastAPI + LangChain that exposes a single `POST /api/chat` endpoint and a `GET /health` readiness probe.
- **JWT validation + forwarding**: The chatbot validates incoming JWTs (using the same signing key as the upstream API) and forwards them to fetch data, ensuring only authenticated users can query.
- **Read-only upstream integration**: The chatbot calls only `GET` endpoints on the Air Project API — it never creates, updates, or deletes data.
- **LLM-powered query interpretation**: LangChain agents/tools interpret the user's question, decide which upstream air quality endpoints to call, and compose a human-friendly response.
- **Language-aware responses**: The chatbot fetches the user's language preference (`GET /api/preferences/me`) and responds in `ES` or `EN` accordingly.
- **OpenAPI spec**: A Swagger file (`openapi-chatbot.yaml`) defining the chatbot's API contract is already created.

## Capabilities

### New Capabilities
- `chat-endpoint`: Single `POST /api/chat` endpoint that accepts a natural-language message and returns an AI-generated answer about air quality data.
- `jwt-auth`: JWT validation on incoming requests and token forwarding to the upstream Air Project API for data fetching.
- `air-quality-tools`: LangChain tools that wrap the upstream `GET /api/air-quality/current` and `GET /api/air-quality/historical` endpoints for the LLM agent to invoke.
- `language-detection`: Automatic detection of user language preference via `GET /api/preferences/me` to respond in Spanish or English.

### Modified Capabilities
_(none — this is a new standalone service)_

## Impact

- **New service**: A Python FastAPI application running on port `8000`, deployed alongside the existing Java backend on port `8080`.
- **Dependencies**: `fastapi`, `uvicorn`, `langchain`, `langchain-openai` (or similar LLM provider), `httpx` (async HTTP client), `pyjwt` (JWT validation).
- **Infrastructure**: Requires an LLM API key (e.g., OpenAI) configured via environment variables.
- **Upstream API**: No changes to the existing Air Project backend. The chatbot is a pure consumer of read-only endpoints.
- **Network**: The chatbot must be able to reach `http://localhost:8080` (or the configured upstream URL).
