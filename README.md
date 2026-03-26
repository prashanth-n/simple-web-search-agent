# Web Research MCP

Production-oriented starter for a web research workflow with a FastAPI backend, PostgreSQL persistence, Ollama Cloud summarization, and a React + Vite frontend.

## Structure

```text
.
├── backend/
├── frontend/
├── docker-compose.yml
└── README.md
```

## Backend

- `GET /` returns a health payload.
- `GET /research?query=...` runs the research agent.
- Agent flow: DuckDuckGo search -> page scrape -> Ollama Cloud summary.
- Research queries and result payloads are stored in PostgreSQL through SQLAlchemy.

## Local Setup

### 1. Configure environment

Copy `backend/.env.example` to `backend/.env` and set a valid `OLLAMA_API_KEY`.

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
uv run uvicorn app.main:app --reload
```

## Example request

```bash
curl "http://localhost:8000/research?query=latest%20battery%20storage%20market%20trends"
```

## Notes

- Ollama Cloud API requests are sent to `https://ollama.com/api/generate` with bearer-token authentication.
- The default model is `llama3`, configurable via `OLLAMA_MODEL`.
- The frontend uses reusable button, input, and card primitives in a shadcn-style component pattern inside `Search.jsx`.
