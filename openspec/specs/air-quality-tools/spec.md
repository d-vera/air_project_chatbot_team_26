# air-quality-tools Specification

## Purpose
TBD - created by archiving change langchain-chatbot-backend. Update Purpose after archive.
## Requirements
### Requirement: Current air quality tool
The system SHALL provide a LangChain tool named `get_current_air_quality` that calls `GET /api/air-quality/current` on the upstream API. The tool SHALL accept an optional `deviceId` parameter to filter by device. The tool SHALL return the raw JSON data (temperature, humidity, CO₂, PM1.0, PM2.5, PM10) for the LLM to interpret.

#### Scenario: Fetch current readings for all devices
- **WHEN** the LLM agent invokes the `get_current_air_quality` tool without a `deviceId`
- **THEN** the tool SHALL call `GET /api/air-quality/current` and return the latest readings for all devices

#### Scenario: Fetch current readings for a specific device
- **WHEN** the LLM agent invokes the `get_current_air_quality` tool with a `deviceId`
- **THEN** the tool SHALL call `GET /api/air-quality/current?deviceId={deviceId}` and return the readings for that device

### Requirement: Historical air quality tool
The system SHALL provide a LangChain tool named `get_historical_air_quality` that calls `GET /api/air-quality/historical` on the upstream API. The tool SHALL accept parameters for `range` (LAST_DAY, LAST_WEEK, LAST_MONTH, LAST_YEAR) or custom date range (`from`, `to`), and an optional `deviceId`.

#### Scenario: Fetch historical data with predefined range
- **WHEN** the LLM agent invokes the `get_historical_air_quality` tool with `range=LAST_WEEK`
- **THEN** the tool SHALL call `GET /api/air-quality/historical?range=LAST_WEEK` and return the aggregated data

#### Scenario: Fetch historical data with custom date range
- **WHEN** the LLM agent invokes the `get_historical_air_quality` tool with `from` and `to` date parameters
- **THEN** the tool SHALL call `GET /api/air-quality/historical?from={from}&to={to}` and return the aggregated data

#### Scenario: Fetch historical data for a specific device
- **WHEN** the LLM agent invokes the `get_historical_air_quality` tool with a `deviceId` and a `range`
- **THEN** the tool SHALL call `GET /api/air-quality/historical?range={range}&deviceId={deviceId}` and return the filtered data

### Requirement: Read-only enforcement
The LangChain tools SHALL only call HTTP GET endpoints on the upstream API. No tool SHALL perform POST, PUT, PATCH, or DELETE operations.

#### Scenario: No write operations
- **WHEN** the LLM agent processes any user question
- **THEN** only GET requests SHALL be made to the upstream API

### Requirement: Tools use forwarded JWT
All LangChain tools SHALL use the authenticated user's JWT token when making upstream API calls.

#### Scenario: Tool authenticates with upstream
- **WHEN** any LangChain tool makes a request to the upstream API
- **THEN** the request SHALL include the user's JWT in the `Authorization: Bearer <token>` header

