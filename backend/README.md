Backend (FastAPI)
Overview
Implements the API for analysis, comparable discovery, financial enrichment (FMP), and a simple RAG assistant.

Docs

- Root usage and setup: see ../../README.md
- Full API reference: ./API_DOCUMENTATION.md

Run

- pip install -r requirements.txt
- python main.py # http://localhost:8000

Env (.env)

- DEEPSEEK_API_KEY=... (current provider)
- GEMINI_API_KEY=... (planned provider)
- FMP_API_KEY=...
- API_HOST=0.0.0.0 (optional)
- API_PORT=8000 (optional)
- DEBUG=true (optional)

Key files

- routes/: modular endpoints (analysis, market, companies, comparison, rag)
- deepseek_api.py, fmp_api.py: external clients
- rag_service.py: minimal RAG engine (sentence-transformers + FAISS)
