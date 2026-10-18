## ADDED Requirements

### Requirement: Fetch user language preference
The system SHALL call `GET /api/preferences/me` on the upstream API (using the forwarded JWT) to retrieve the authenticated user's language preference before generating a response.

#### Scenario: User has Spanish preference
- **WHEN** a user with language preference `ES` sends a chat message
- **THEN** the system SHALL detect the `ES` preference and generate the response in Spanish

#### Scenario: User has English preference
- **WHEN** a user with language preference `EN` sends a chat message
- **THEN** the system SHALL detect the `EN` preference and generate the response in English

### Requirement: Default language fallback
The system SHALL default to `EN` (English) if the preferences endpoint is unreachable or returns no language preference.

#### Scenario: Preferences endpoint fails
- **WHEN** the upstream `GET /api/preferences/me` endpoint returns an error or is unreachable
- **THEN** the system SHALL default to English (`EN`) and continue processing the chat message without failing

#### Scenario: No language preference set
- **WHEN** the user's preference response does not include a `language` field or it is null
- **THEN** the system SHALL default to English (`EN`)

### Requirement: Language included in response
The system SHALL include the detected language (`ES` or `EN`) in the chat response body under the `language` field.

#### Scenario: Response includes language field
- **WHEN** the system successfully generates a chat response
- **THEN** the response body SHALL include a `language` field with the value `ES` or `EN` matching the language used in the `reply`

### Requirement: LLM system prompt includes language directive
The system SHALL include a language directive in the LangChain system prompt instructing the LLM to respond in the detected language.

#### Scenario: System prompt set to Spanish
- **WHEN** the detected user language is `ES`
- **THEN** the LLM system prompt SHALL include a directive to respond in Spanish

#### Scenario: System prompt set to English
- **WHEN** the detected user language is `EN`
- **THEN** the LLM system prompt SHALL include a directive to respond in English
