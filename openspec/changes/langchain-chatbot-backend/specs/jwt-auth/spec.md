## ADDED Requirements

### Requirement: Validate JWT on every chat request
The system SHALL validate the JWT token from the `Authorization: Bearer <token>` header on every `POST /api/chat` request. Validation MUST check the token signature and expiration. The JWT secret/key SHALL be configured via the `JWT_SECRET` environment variable.

#### Scenario: Valid JWT accepted
- **WHEN** a user sends a chat request with a valid, non-expired JWT in the `Authorization` header
- **THEN** the system SHALL accept the request and proceed with processing the chat message

#### Scenario: Missing JWT rejected
- **WHEN** a user sends a chat request without an `Authorization` header
- **THEN** the system SHALL return HTTP 401 with `{ "error": "unauthorized", "message": "Invalid or expired JWT token" }`

#### Scenario: Expired JWT rejected
- **WHEN** a user sends a chat request with an expired JWT
- **THEN** the system SHALL return HTTP 401 with `{ "error": "unauthorized", "message": "Invalid or expired JWT token" }`

#### Scenario: Malformed JWT rejected
- **WHEN** a user sends a chat request with a malformed or tampered JWT
- **THEN** the system SHALL return HTTP 401 with `{ "error": "unauthorized", "message": "Invalid or expired JWT token" }`

### Requirement: Forward JWT to upstream API calls
The system SHALL forward the original JWT token in the `Authorization: Bearer <token>` header when making any request to the upstream Air Project API. The system SHALL NOT create, modify, or forge tokens.

#### Scenario: JWT forwarded to upstream
- **WHEN** the system calls any upstream Air Project API endpoint
- **THEN** the request SHALL include the original user JWT in the `Authorization` header

### Requirement: Fail fast on missing JWT secret
The system SHALL fail to start if the `JWT_SECRET` environment variable is not set.

#### Scenario: Missing JWT secret on startup
- **WHEN** the application starts without `JWT_SECRET` configured
- **THEN** the system SHALL raise an error and refuse to start
