# WARP quick guide (expanded)

Use the root README for full details. This file is a focused, copy‑pasteable quickstart for Warp CLI and LLMs.

## What this is

- Backend: FastAPI API in `backend/` (analysis, comparables, FMP metrics, simple RAG)
- Frontend: Next.js app in `frontend/` (forms, results, comparison table, chatbot)
- LLM providers: DeepSeek (current), Gemini (planned)

## Prereqs

- Python 3.10+
- Node.js 18+

## Setup

```zsh
# Backend deps
pip install -r backend/requirements.txt

# Env (never commit .env)
cp backend/.env.example backend/.env
# Fill: DEEPSEEK_API_KEY, (optional) GEMINI_API_KEY, FMP_API_KEY

# Frontend deps
cd frontend && npm install
```

## Run (two panes)

```zsh
# Pane 1 (API)
python backend/main.py  # http://localhost:8000

# Alternative
# uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Pane 2 (Web)
npm run dev --prefix frontend  # http://localhost:3000

# If backend URL differs:
# export NEXT_PUBLIC_API_BASE="http://localhost:8000"
```

## Quick API checks

```zsh
# Health
curl -s http://localhost:8000/health

# Analyze company (name + website)
curl -sX POST http://localhost:8000/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"name":"Acme AI","website":"https://example.com"}'

# Find comparables (flexible input)
curl -sX POST http://localhost:8000/api/find-comparables \
  -H 'Content-Type: application/json' \
  -d '{"company_name":"Acme AI","count":10}'

# Comparables with financials (requires FMP_API_KEY)
curl -sX POST http://localhost:8000/api/comparables-with-financials \
  -H 'Content-Type: application/json' \
  -d '{"company_name":"Acme AI","include_financials":true,"count":10}'
```

Endpoints (brief): `/api/analyze`, `/api/find-comparables`, `/api/comparables-with-financials`, `/api/refine-comparables`, `/api/filter-options`, `/api/market/profile/{ticker}`. See `backend/API_DOCUMENTATION.md` for full details.

## Testing shortcuts

```zsh
# From repo root
python backend/test_deepseek_api.py
python backend/test_rag.py
```

## Common env

- Backend `.env`: `DEEPSEEK_API_KEY`, `GEMINI_API_KEY` (optional), `FMP_API_KEY`, `DEEPSEEK_API_URL?`, `API_HOST?`, `API_PORT?`, `DEBUG?`
- Frontend: `NEXT_PUBLIC_API_BASE` (default http://localhost:8000)

## Troubleshooting

- 401/403 from API calls: check API keys in `backend/.env` and that backend restarted
- 5xx on analysis: missing/invalid DEEPSEEK_API_KEY or upstream error; inspect backend logs
- No financials: ensure `FMP_API_KEY` is set
- CORS in browser: backend allows http://localhost:3000 by default (see `backend/main.py`)
- Port conflicts: change `API_PORT` or pass `--port` to uvicorn; update `NEXT_PUBLIC_API_BASE`

## Provider notes

- DeepSeek is wired today (`backend/deepseek_api.py`)
- Gemini support is planned; keep `GEMINI_API_KEY` ready (no runtime toggle yet)
