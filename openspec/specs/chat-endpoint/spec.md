# chat-endpoint Specification

## Purpose
TBD - created by archiving change langchain-chatbot-backend. Update Purpose after archive.
## Requirements
### Requirement: Accept chat messages via POST endpoint
The system SHALL expose a `POST /api/chat` endpoint that accepts a JSON body with a `message` field (string, 1–1000 characters) and returns a JSON response with `reply` (string) and `language` (enum: `ES`, `EN`).

#### Scenario: Successful chat request
- **WHEN** a user sends a POST request to `/api/chat` with body `{ "message": "What is the current temperature?" }` and a valid JWT in the `Authorization` header
- **THEN** the system SHALL return HTTP 200 with a JSON body containing a natural-language `reply` answering the question and a `language` field matching the user's preference

#### Scenario: Empty message rejected
- **WHEN** a user sends a POST request to `/api/chat` with body `{ "message": "" }` or a missing `message` field
- **THEN** the system SHALL return HTTP 422 with an error response containing `error` and `message` fields

#### Scenario: Message exceeds maximum length
- **WHEN** a user sends a POST request to `/api/chat` with a `message` longer than 1000 characters
- **THEN** the system SHALL return HTTP 422 with an appropriate error message

### Requirement: Health check endpoint
The system SHALL expose a `GET /health` endpoint that returns HTTP 200 with `{ "status": "ok", "version": "1.0.0" }`. This endpoint SHALL NOT require authentication.

#### Scenario: Health check returns ok
- **WHEN** any client sends a GET request to `/health`
- **THEN** the system SHALL return HTTP 200 with a JSON body containing `status` as `"ok"` and the API `version`

### Requirement: Greet user by name
The system SHALL fetch the user's profile via `GET /api/users/me` (using the forwarded JWT) and include a personalized greeting using the user's `firstName` at the beginning of the reply.

#### Scenario: User greeted by first name
- **WHEN** a user named "Carlos" sends a chat message
- **THEN** the system SHALL include a greeting using "Carlos" at the beginning of the reply (e.g., "Hola Carlos, ..." or "Hi Carlos, ...")

#### Scenario: Profile fetch fails gracefully
- **WHEN** the upstream `GET /api/users/me` endpoint returns an error or is unreachable
- **THEN** the system SHALL continue processing the chat message without a personalized greeting and not fail the request

### Requirement: Upstream API unreachable handling
The system SHALL return HTTP 502 (Bad Gateway) when the upstream Air Project API is unreachable or returns a connection error.

#### Scenario: Upstream API is down
- **WHEN** a user sends a valid chat request but the upstream API at the configured URL is unreachable
- **THEN** the system SHALL return HTTP 502 with `{ "error": "bad_gateway", "message": "Unable to reach the Air Project API" }`

### Requirement: LLM processing failure handling
The system SHALL return HTTP 500 (Internal Server Error) when the LLM provider fails or returns an error.

#### Scenario: LLM API error
- **WHEN** a user sends a valid chat request but the LLM provider returns an error
- **THEN** the system SHALL return HTTP 500 with `{ "error": "internal_error", "message": "An unexpected error occurred while processing your request" }`

