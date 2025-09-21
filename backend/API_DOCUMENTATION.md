# AI Analyst for Startup and Enterprise Evaluation — API Documentation

## Overview

This API provides endpoints for AI-driven company evaluation across startups and enterprises. It analyzes a target company, finds comparable public peers, enriches results with financial metrics, and offers a RAG-powered assistant for interactive insights.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API uses API keys for external services (DeepSeek, FMP) but doesn't require authentication for the main endpoints.

## Core Endpoints

### 1. Find Comparables (Main Endpoint)

**POST** `/api/find-comparables`

This is the main endpoint that implements the core README requirements:

- Takes flexible input: company ID, name, or website
- Analyzes the company using DeepSeek API
- Finds 7-10 comparable public companies
- Returns comprehensive results

**Request Body (Flexible Input Options):**

**Option 1: Company ID from database**

```json
{
  "company_id": "tech_innovations_1",
  "count": 10
}
```

**Option 2: Company name and website**

```json
{
  "company_name": "Tech Innovations Inc.",
  "company_website": "https://techinnovations.example.com",
  "count": 10
}
```

**Option 3: Company name only**

```json
{
  "company_name": "Tech Innovations Inc.",
  "count": 10
}
```

**Option 4: Company website only**

```json
{
  "company_website": "https://techinnovations.example.com",
  "count": 10
}
```

**Response:**

```json
{
  "target_company": {
    "id": "tech_innovations_1",
    "name": "Tech Innovations Inc.",
    "website": "https://techinnovations.example.com",
    "description": "Comprehensive company description..."
  },
  "comparable_companies": [
    {
      "name": "Microsoft Corporation",
      "ticker": "MSFT",
      "rationale": "Both companies focus on enterprise software solutions and AI technologies."
    }
  ],
  "analysis_timestamp": "2024-01-01T00:00:00Z",
  "input_type": "company_id"
}
```

### 2. Company Analysis

**POST** `/api/analyze`

Analyzes a company based on name and website to generate a comprehensive description.

**Request Body:**

```json
{
  "name": "Tech Innovations Inc.",
  "website": "https://techinnovations.example.com"
}
```

**Response:**

```json
{
  "name": "Tech Innovations Inc.",
  "website": "https://techinnovations.example.com",
  "description": "Comprehensive company description...",
  "industry": "Technology",
  "business_model": "SaaS"
}
```

### 3. Find Comparable Companies

**POST** `/api/comparable`

Finds comparable companies based on a company description.

**Request Body:**

```json
{
  "company_description": "Comprehensive company description...",
  "count": 10
}
```

**Response:**

```json
{
  "target_company": "Tech Innovations Inc.",
  "comparable_companies": [
    {
      "name": "Microsoft Corporation",
      "ticker": "MSFT",
      "rationale": "Both companies focus on enterprise software solutions..."
    }
  ]
}
```

## Extension 1: Financial Metrics Integration

### 4. Find Comparables with Financial Data

**POST** `/api/comparables-with-financials`

Enhanced version of the main endpoint that includes financial metrics (market cap, EBITDA, revenue) for each comparable company using FMP API integration.

**Request Body (Flexible Input Options):**

**Option 1: Company ID from database**

```json
{
  "company_id": "tech_innovations_1",
  "include_financials": true,
  "count": 10
}
```

**Option 2: Company name and website**

```json
{
  "company_name": "Tech Innovations Inc.",
  "company_website": "https://techinnovations.example.com",
  "include_financials": true,
  "count": 10
}
```

**Option 3: Company name only**

```json
{
  "company_name": "Tech Innovations Inc.",
  "include_financials": true,
  "count": 10
}
```

**Option 4: Company website only**

```json
{
  "company_website": "https://techinnovations.example.com",
  "include_financials": true,
  "count": 10
}
```

**Response:**

```json
{
  "target_company": {
    "id": "tech_innovations_1",
    "name": "Tech Innovations Inc.",
    "website": "https://techinnovations.example.com",
    "description": "Comprehensive company description..."
  },
  "comparable_companies": [
    {
      "name": "Microsoft Corporation",
      "ticker": "MSFT",
      "rationale": "Both companies focus on enterprise software solutions...",
      "financial_metrics": {
        "ticker": "MSFT",
        "company_name": "Microsoft Corporation",
        "market_cap": 2500000000000,
        "enterprise_value": 2600000000000,
        "revenue": 198270000000,
        "ebitda": 85000000000,
        "net_income": 72361000000,
        "current_price": 330.5,
        "currency": "USD"
      }
    }
  ],
  "financial_data_included": true,
  "note": "Financial metrics provided by FMP API integration",
  "input_type": "company_id"
}
```

## Extension 2: Interactive Refinement

### 5. Refine Comparable Search

**POST** `/api/refine-comparables`

Allows users to provide feedback and refine the search results to find additional comparable companies.

**Request Body:**

```json
{
  "original_request": {
    "company_description": "Original company description..."
  },
  "user_feedback": "I need more companies in the healthcare sector",
  "refinement_type": "industry",
  "additional_count": 5
}
```

**Response:**

```json
{
  "original_request": {
    "company_description": "Original company description..."
  },
  "user_feedback": "I need more companies in the healthcare sector",
  "refinement_type": "industry",
  "additional_companies": [
    {
      "name": "Johnson & Johnson",
      "ticker": "JNJ",
      "rationale": "Healthcare sector focus with similar business model..."
    }
  ],
  "refinement_timestamp": "2024-01-01T00:00:00Z"
}
```

### 6. Get Refinement Suggestions

**GET** `/api/refinement-suggestions`

Returns available refinement options for interactive search.

**Response:**

```json
{
  "refinement_types": [
    {
      "type": "industry",
      "description": "Focus on specific industry sectors",
      "examples": ["technology", "healthcare", "finance", "retail"]
    },
    {
      "type": "size",
      "description": "Filter by company size",
      "examples": ["small cap", "mid cap", "large cap", "enterprise"]
    },
    {
      "type": "geography",
      "description": "Focus on specific geographic regions",
      "examples": ["North America", "Europe", "Asia", "emerging markets"]
    },
    {
      "type": "business_model",
      "description": "Filter by business model",
      "examples": ["SaaS", "e-commerce", "marketplace", "subscription"]
    }
  ]
}
```

## Additional Endpoints

### 7. Health Check

**GET** `/health`

Returns API health status.

**Response:**

```json
{
  "status": "healthy"
}
```

### 8. Company Management Endpoints

#### Get All Companies

**GET** `/api/companies`

#### Get Company by ID

**GET** `/api/companies/{company_id}`

#### Create Company

**POST** `/api/companies`

#### Update Company

**PUT** `/api/companies/{company_id}`

#### Delete Company

**DELETE** `/api/companies/{company_id}`

### 9. Company Comparison

**GET** `/api/compare?company_ids=company1&company_ids=company2`

## Environment Variables

The following environment variables are required:

```bash
# DeepSeek API for company analysis
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_URL=https://api.deepseek.com/v1

# FMP API for financial metrics (Extension 1)
FMP_API_KEY=your_fmp_api_key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (company not found)
- `500`: Internal Server Error

Error responses include a detail message:

```json
{
  "detail": "Error message describing the issue"
}
```

## Rate Limiting

Currently, there are no rate limits implemented, but consider implementing them for production use.

## CORS

The API is configured to allow cross-origin requests from `http://localhost:3000` for frontend integration.

## Usage Examples

### Basic Usage (Core Requirements)

**Using Company ID:**

```bash
curl -X POST "http://localhost:8000/api/find-comparables" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "tech_innovations_1",
    "count": 10
  }'
```

**Using Company Name and Website:**

```bash
curl -X POST "http://localhost:8000/api/find-comparables" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tech Innovations Inc.",
    "company_website": "https://techinnovations.example.com",
    "count": 10
  }'
```

**Using Company Name Only:**

```bash
curl -X POST "http://localhost:8000/api/find-comparables" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tech Innovations Inc.",
    "count": 10
  }'
```

**Using Company Website Only:**

```bash
curl -X POST "http://localhost:8000/api/find-comparables" \
  -H "Content-Type: application/json" \
  -d '{
    "company_website": "https://techinnovations.example.com",
    "count": 10
  }'
```

### With Financial Metrics (Extension 1)

**Using Company ID:**

```bash
curl -X POST "http://localhost:8000/api/comparables-with-financials" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "tech_innovations_1",
    "include_financials": true,
    "count": 10
  }'
```

**Using Company Name and Website:**

```bash
curl -X POST "http://localhost:8000/api/comparables-with-financials" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tech Innovations Inc.",
    "company_website": "https://techinnovations.example.com",
    "include_financials": true,
    "count": 10
  }'
```

### Interactive Refinement (Extension 2)

```bash
curl -X POST "http://localhost:8000/api/refine-comparables" \
  -H "Content-Type: application/json" \
  -d '{
    "original_request": {"company_description": "Original description..."},
    "user_feedback": "Need more healthcare companies",
    "refinement_type": "industry",
    "additional_count": 5
  }'
```
