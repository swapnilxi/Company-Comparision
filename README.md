# AI Analyst for Startup and Enterprise Evaluation

An end-to-end AI application that evaluates startups and enterprises, finds comparable public peers, enriches with financial metrics, and lets you interact with results via a RAG chatbot.

## Highlights

- AI-driven analysis of a target company (name/website/ticker)
- Comparable company discovery (7–10 peers) with rationale
- Optional financial enrichment via FMP (market cap, revenue, EBITDA, ratios)
- Interactive refinement loop and filterable results
- RAG chatbot for follow-up questions and insights
- Full-stack: FastAPI backend + Next.js frontend

## Architecture

- Backend: FastAPI (Python)
  - DeepSeek API client for analysis and comparables
  - FMP API client for market/financial data
  - RAG service using sentence-transformers + FAISS
  - Modular route structure under `backend/routes`
- Frontend: Next.js (App Router, TypeScript)
  - Company input, results view, comparison table, filters
  - RAG chatbot UI component
  - TailwindCSS for styling

Directory overview:

- `/backend` — FastAPI app, routes, models, external API clients
- `/frontend` — Next.js app with components and pages

## Key Features

- Flexible input:
  - Company name + website
  - Ticker symbol (auto-fetch profile)
  - Company ID from DB (sample)
- Outputs:
  - Target company analysis (description, highlights)
  - 7–10 comparable public companies with name, ticker, and rationale
  - Optional detailed financials and ratios (via FMP)
- Comparison Table:
  - Select companies to compare
  - Toggle target company inclusion
  - Request detailed metrics and ratios
  - Filter by size/geography/characteristics/sectors (simplified demo)
- RAG Chatbot:
  - Ask questions about results and metrics
  - Gets smarter with vector search over analysis and comparison context

## Getting Started

Prereqs:

- Python 3.10+
- Node.js 18+

### 1) Backend

1. Move to backend folder and install dependencies
   - pip install -r backend/requirements.txt
2. Create `backend/.env` with:
   - DEEPSEEK_API_KEY=...
   - FMP_API_KEY=...
   - API_HOST=0.0.0.0 (optional)
   - API_PORT=8000 (optional)
   - DEBUG=true (optional)
3. Run the API
   - python backend/main.py

### 2) Frontend

1. Move to frontend folder and install deps
   - cd frontend
   - npm install
2. Start dev server
   - npm run dev
3. By default, the frontend requests `http://localhost:8000`. To change, set `NEXT_PUBLIC_API_BASE` in env.

## Core API Endpoints (brief)

- POST `/api/analyze` — Analyze target company (name+website)
- POST `/api/find-comparables` — Flexible entry (id/name/website/ticker) → comparables
- POST `/api/comparables-with-financials` — Comparables + financials
- POST `/api/refine-comparables` — Interactive refinement
- GET `/api/filter-options` — Filter presets
- GET `/api/market/profile/{ticker}` — Company profile via FMP
- GET `/health` — Health check

Full details in `backend/API_DOCUMENTATION.md`.

## Configuration Notes

- CORS is enabled for `http://localhost:3000` by default (see `backend/main.py`).
- RAG embeddings use `sentence-transformers`; FAISS is used for similarity search.
- External API clients are in `backend/deepseek_api.py` and `backend/fmp_api.py`.

## Development Tips

- Start backend and frontend in separate terminals.
- Use the Results View to pick companies; switch to Comparison Table to compare.
- Click "Get Detailed Data" to fetch richer metrics.
- Open the chatbot to query the analysis and comparison context.

## Roadmap

- Auth + rate limiting
- Persisted vector store and history
- Export reports (PDF/CSV)
- More granular filters and sector tagging

## License

MIT or project-specific; adjust as needed.
