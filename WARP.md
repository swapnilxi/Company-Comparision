# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This repository contains "AI Analyst for Startup and Enterprise Evaluation" — an application that evaluates startups and enterprises using AI. It analyzes a target company, identifies comparable public peers, and can enrich results with financial metrics. It uses AI-powered analysis (DeepSeek API) and optional financial data via FMP API, plus a RAG chatbot for interactive insights.

**Architecture**: Full-stack application with Python FastAPI backend and Next.js frontend

## Common Development Commands

### Backend (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server (with hot reload)
python main.py

# Run production server
uvicorn main:app --host 0.0.0.0 --port 8000

# Test API endpoints
python ../test_deepseek_api.py

# Check API health
curl http://localhost:8000/health

# Run a single API test function (modify test_deepseek_api.py as needed)
python -c "from test_deepseek_api import test_analyze_company; test_analyze_company()"
```

### Frontend (Next.js)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server (with hot reload and turbopack)
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Lint code
npm run lint
```

### Full Application

```bash
# Start both services (run in separate terminals)
# Terminal 1 - Backend
cd backend && python main.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

## High-Level Architecture

### Backend Structure (`/backend`)

- **FastAPI Application** (`main.py`): Main app entry point with CORS middleware, router includes
- **Route Modules** (`/routes`): Modular API endpoints organized by feature
  - `health.py`: System health checks
  - `analysis.py`: Company analysis endpoints
  - `companies.py`: CRUD operations for company data
  - `comparison.py`: Company comparison functionality
  - `market.py`: Market data and financial metrics
- **Data Models** (`models.py`): Pydantic models for request/response validation and data structures
- **External APIs** (`deepseek_api.py`, `fmp_api.py`): Client classes for third-party service integration
- **Database Layer** (`database.py`): Data persistence logic

### Frontend Structure (`/frontend`)

- **Next.js 15 App Router**: Modern React framework with TypeScript
- **Main Page** (`/src/app/page.tsx`): Single-page interface with company input forms and results display
- **Components** (`/src/components`): Reusable UI components (CompanyCard, ComparisonChart)
- **Utilities** (`/src/utils`): Helper functions and analytics utils
- **Styling**: TailwindCSS v4 with dark mode support

### API Integration Flow

1. **Company Analysis**: User input (name/website/ticker) → DeepSeek API → Structured company description
2. **Comparable Finding**: Company description → DeepSeek API → List of comparable public companies
3. **Financial Enhancement**: Company tickers → FMP API → Financial metrics (market cap, revenue, EBITDA)

### Key Features

- **Flexible Input**: Supports company name, website URL, stock ticker, or internal company ID
- **AI-Powered Analysis**: Uses DeepSeek API for intelligent company analysis and comparable identification
- **Financial Integration**: Optional FMP API integration for real-time financial metrics
- **Interactive Refinement**: User feedback system to improve search results
- **Multiple Search Modes**: Analysis-only, basic comparison, or comparison with financial data

### Environment Configuration

Backend requires environment variables in `/backend/.env`:

- `DEEPSEEK_API_KEY`: Required for AI-powered company analysis
- `FMP_API_KEY`: Required for financial metrics (Extension 1)
- `API_HOST`, `API_PORT`, `DEBUG`: FastAPI server configuration

Frontend API base URL configured via `NEXT_PUBLIC_API_BASE` (defaults to `http://localhost:8000`)

### Core API Endpoints

- `POST /api/analyze`: Generate comprehensive company description
- `POST /api/find-comparables`: Main endpoint - find comparable companies (flexible input)
- `POST /api/comparables-with-financials`: Enhanced endpoint with financial metrics
- `POST /api/refine-comparables`: Interactive search refinement
- Standard CRUD operations for company management

### Data Flow Patterns

The application supports multiple input patterns with intelligent fallbacks:

1. **Primary**: Stock ticker → auto-populate company data → analysis/comparison
2. **Standard**: Company name + website → structured analysis → comparable search
3. **Flexible**: Any combination of name, website, company ID → best-effort matching
4. **Refinement**: Previous results + user feedback → improved comparable suggestions

### External Dependencies

- **DeepSeek API**: Company analysis and comparable finding (required)
- **FMP API**: Real-time financial data and stock quotes (optional for Extension 1)
- **CORS**: Configured for localhost:3000 frontend integration

This architecture enables rapid development of company analysis features while maintaining clear separation between AI-powered analysis, financial data integration, and user interface components.
