# AI Analyst: Company Comparison (FastAPI + Next.js)

Analyze a target company, find 7–10 comparable public peers, enrich with financials (FMP), and chat over results with a simple RAG assistant.

## TL;DR for LLMs / Wrap CLI

```yaml
project:
  name: company-comparison-ai
  stack: fastapi (python) + next.js (typescript)
  key-dirs:
    backend: fastapi app, routes, models, api clients
    frontend: next.js app with ui components
  llm-providers:
    - deepseek (current)
    - gemini (planned)
  env:
    backend:
      [
        DEEPSEEK_API_KEY,
        GEMINI_API_KEY,
        FMP_API_KEY,
        API_HOST?,
        API_PORT?,
        DEBUG?,
      ]
    frontend: [NEXT_PUBLIC_API_BASE]
  run:
    - backend: pip install -r backend/requirements.txt && python backend/main.py
    - frontend: cd frontend && npm install && npm run dev
docs:
  api: backend/API_DOCUMENTATION.md
```

## Features

- Input: company name/website or ticker (ID supported in demo DB)
- Output: 7–10 comparable public companies with rationale
- Optional financial metrics via FMP: market cap, revenue, EBITDA, ratios
- Comparison table + basic filters (size, geography, characteristics, sector)
- RAG chatbot for contextual Q&A over analysis/comparison

## Repo Layout

- `backend/` FastAPI app, modular routes, models, DeepSeek + FMP clients, basic RAG
- `frontend/` Next.js (App Router, TS), UI components and pages

## Quickstart

Prereqs: Python 3.10+, Node.js 18+

Backend

- Create env: copy `backend/.env.example` to `backend/.env` and fill keys
- Install deps: pip install -r backend/requirements.txt
- Run API: python backend/main.py (defaults to http://localhost:8000)

Frontend

- cd frontend && npm install
- npm run dev (defaults to http://localhost:3000)
- Configure API base (optional): set `NEXT_PUBLIC_API_BASE` if backend URL differs

## Environment Variables

Backend (`backend/.env`)

- DEEPSEEK_API_KEY=...
- GEMINI_API_KEY=... # planned provider; see note below
- FMP_API_KEY=...
- DEEPSEEK_API_URL=https://api.deepseek.com/v1 # optional
- API_HOST=0.0.0.0 # optional
- API_PORT=8000 # optional
- DEBUG=true # optional

Frontend

- NEXT_PUBLIC_API_BASE=http://localhost:8000

Provider notes

- Current implementation uses DeepSeek (`backend/deepseek_api.py`).
- Gemini support is planned; `GEMINI_API_KEY` is reserved for that integration.

## API (brief)

- POST `/api/analyze` — analyze a company (name + website)
- POST `/api/find-comparables` — flexible input → comparable companies
- POST `/api/comparables-with-financials` — comparables + financial metrics
- POST `/api/refine-comparables` — refine results via feedback
- GET `/api/filter-options` — filter presets for UI
- GET `/api/market/profile/{ticker}` — profile via FMP
- GET `/health` — health check

Details: see `backend/API_DOCUMENTATION.md`.

## Dev Notes

- CORS allows http://localhost:3000 (see `backend/main.py`).
- RAG uses sentence-transformers + FAISS (simple, optional path).
- Tests: `backend/test_deepseek_api.py`, `backend/test_rag.py`.

## Roadmap

- Switchable LLM provider (DeepSeek | Gemini)
- Persisted vector store and conversation history
- Export (CSV/PDF) and richer filters

## License

MIT (update as needed)
