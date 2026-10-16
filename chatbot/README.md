# Air Project — Chatbot Backend (Team 26)

A FastAPI and LangChain backend providing a natural language interface for environmental measurements (temperature, humidity, CO₂, PM1.0, PM2.5, PM10) from the Air Project ecosystem (`http://localhost:8080`).

## Features

- **Read-Only**: Strictly queries air quality data (`GET /api/air-quality/current` and `GET /api/air-quality/historical`). Never executes mutations or accesses sensor management endpoints.
- **JWT Validation & Forwarding**: Validates incoming bearer tokens locally for fast rejection of invalid/expired tokens, and forwards the token to upstream requests.
- **Personalized & Language-Aware**: Queries user preferences (`GET /api/preferences/me`) to reply in `ES` or `EN`, and user profile (`GET /api/users/me`) to greet the user by name.
- **LangChain Tool-Calling Agent**: Dynamically invokes the appropriate air quality tools based on the user's question.

---

## Architecture

```
┌──────────┐   POST /api/chat (JWT)   ┌──────────────────────┐  GET only (JWT)   ┌──────────────┐
│  Client  │ ───────────────────────▶ │  Chatbot Service     │ ────────────────▶ │  Air Project │
│          │ ◀─────────────────────── │  (FastAPI:8000)      │ ◀──────────────── │  Backend     │
│          │   Reply (ES/EN)          │  LangChain + Tools   │   Readings JSON   │  (:8080)     │
└──────────┘                          └──────────┬───────────┘                   └──────────────┘
                                                 │
                                                 ▼
                                           ┌──────────┐
                                           │   LLM    │
                                           │ (OpenAI) │
                                           └──────────┘
```

---

## Setup & Installation

### 1. Requirements

- Python 3.10+
- Access to the upstream Air Project backend (running at `http://localhost:8080`)
- LLM API key (e.g. OpenAI)

### 2. Install Dependencies

```bash
cd chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the `chatbot/` directory (or copy from `.env.example`):

```bash
cp .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `JWT_SECRET` | Secret key used to sign/validate upstream JWT tokens (**Required**) | — |
| `DEEPSEEK_API_KEY` | DeepSeek API key for LangChain agent (**Required**) | — |
| `LLM_BASE_URL` | Base URL for DeepSeek API | `https://api.deepseek.com` |
| `LLM_MODEL` | Model identifier to use with DeepSeek | `deepseek-chat` |
| `UPSTREAM_API_URL` | Base URL of the Air Project backend | `http://localhost:8080` |

---

## Running the Server

Start the application with Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive Swagger UI will be available at:
- `http://localhost:8000/docs`

---

## API Reference

### 1. Health Check
```http
GET /health
```
Response:
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### 2. Chat Endpoint
```http
POST /api/chat
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
  "message": "¿Cuál es la temperatura actual?"
}
```

Response:
```json
{
  "reply": "Hola Carlos, la temperatura actual promedio en los dispositivos es de 21.4°C con una humedad relativa del 58%.",
  "language": "ES"
}
```
