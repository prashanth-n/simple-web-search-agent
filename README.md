# Web Research MCP

Production-oriented starter for a multi-agent web research and chat workflow with a FastAPI backend, PostgreSQL persistence managed by Alembic migrations, cookie-based authentication, Google OAuth, Ollama Cloud summarization, Alpha Vantage market data, and a React + Vite frontend.

## Structure

```text
.
├── backend/
├── frontend/
├── docker-compose.yml
└── README.md
```

## Backend

- `GET /health-check` returns a health payload.
- `POST /auth/signup`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`, `GET /auth/google/login`, and `GET /auth/google/callback` power authentication.
- `GET /agents` returns the available agent catalog.
- `GET /research?query=...&agent_id=...` runs the selected agent for backward-compatible single-turn research.
- `GET /threads?agent_id=...`, `POST /threads`, `GET /threads/{thread_id}/messages`, and `POST /threads/{thread_id}/messages` power persistent multi-agent chat.
- Agent flow: Ollama web search -> Ollama web fetch -> Ollama Cloud summary, with fallback to DuckDuckGo search and HTML scraping.
- The app seeds 5 agents, stores registered users, and scopes agent runs plus persistent chat threads/messages to authenticated users.
- Alembic is the source of truth for schema evolution; the backend container runs `alembic upgrade head` before starting FastAPI.

## Local Setup

### 1. Configure environment

Copy `backend/.env.example` to `backend/.env` and set valid `OLLAMA_API_KEY`, `ALPHA_VANTAGE_API_KEY`, `JWT_SECRET_KEY`, and Google OAuth credentials.

If you have an older local Postgres volume from the pre-Alembic setup, reset it once before starting:

```bash
docker compose down -v
```

### 2. Run with Docker

```bash
docker compose up --build
```

This is the recommended way to start the project locally.

Services started by Docker:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

### 3. Stop the stack

```bash
docker compose down
```

## Optional Manual Development

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

## Example requests

```bash
curl "http://localhost:8000/agents"
curl "http://localhost:8000/research?query=latest%20battery%20storage%20market%20trends&agent_id=1"
curl "http://localhost:8000/threads?agent_id=5"
```

## Notes

- Ollama Cloud API requests are sent to `https://ollama.com/api` with bearer-token authentication.
- Alpha Vantage is used by the `Financial Analyst` agent for company snapshots and chart data.
- Authentication uses an HTTP-only cookie and supports both email/password and Google OAuth login.
- The default Ollama Cloud model is `gpt-oss:120b`, configurable through `OLLAMA_MODEL`.
- The backend seeds `Generic Web Research`, `Startup Analyst`, `Marketing Analyst`, `Product Competitor Analysis`, and `Financial Analyst` with stable IDs.
- The frontend uses Tailwind plus shadcn-style UI primitives, an auth gate, persistent thread navigation, and a charted financial response UI.
