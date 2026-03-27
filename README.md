# Web Research MCP

Production-oriented starter for a multi-agent web research workflow with a FastAPI backend, PostgreSQL persistence, Ollama Cloud summarization, and a React + Vite frontend.

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
- `GET /agents` returns the available agent catalog.
- `GET /research?query=...&agent_id=...` runs the selected agent.
- Agent flow: Ollama web search -> Ollama web fetch -> Ollama Cloud summary, with fallback to DuckDuckGo search and HTML scraping.
- The app seeds 3 agents and stores each agent's runs in a separate table inside one shared PostgreSQL database.

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

## Example requests

```bash
curl "http://localhost:8000/agents"
curl "http://localhost:8000/research?query=latest%20battery%20storage%20market%20trends&agent_id=1"
```

## Notes

- Ollama Cloud API requests are sent to `https://ollama.com/api` with bearer-token authentication.
- All agents use `qwen3:30b` by default through `OLLAMA_MODEL`, and can be changed later per agent.
- The backend seeds `Generic Web Research`, `Startup Analyst`, and `Marketing Analyst` with stable IDs.
- The frontend uses Tailwind plus shadcn-style UI primitives for the sidebar, selector, cards, button, and input.
