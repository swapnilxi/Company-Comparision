# Company Comparison API Guide with DeepSeek Integration

This guide will help you understand how to use the FastAPI-based Company Comparison API with DeepSeek integration.

## Getting Started

### Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.8 or higher
- FastAPI
- Uvicorn
- DeepSeek API key

You can install the required packages using pip:

```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the backend directory with the following variables:

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_URL=https://api.deepseek.com/v1
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### Running the API

To start the API server, navigate to the backend directory and run:

```bash
python main.py
```

Or directly with uvicorn:

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## Using the API

### Interactive Documentation

The API comes with built-in interactive documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

These interfaces allow you to explore and test all available endpoints directly from your browser.

### Step-by-Step Guide

#### 1. View Available Companies

First, let's see what companies are available in the system:

```bash
curl http://localhost:8000/api/companies
```

This will return a list of all companies with their details.

#### 2. Get a Specific Company

To get details about a specific company:

```bash
curl http://localhost:8000/api/companies/company1
```

Replace `company1` with the ID of the company you want to view.

#### 3. Create a New Company

To add a new company to the system:

```bash
curl -X POST http://localhost:8000/api/companies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Tech Startup",
    "industry": "Software",
    "size": "small",
    "founded_year": 2022,
    "description": "An innovative software startup",
    "financial_data": {
      "revenue": 500000.0,
      "profit_margin": 5.0,
      "growth_rate": 30.0,
      "market_share": 1.2
    }
  }'
```

#### 4. Update a Company

To update an existing company's information:

```bash
curl -X PUT http://localhost:8000/api/companies/company1 \
  -H "Content-Type: application/json" \
  -d '{
    "financial_data": {
      "revenue": 5500000.0,
      "growth_rate": 9.5
    }
  }'
```

This example updates only the revenue and growth rate of company1.

#### 5. Compare Companies

To compare multiple companies:

```bash
curl "http://localhost:8000/api/compare?company_ids=company1&company_ids=company2"
```

You can add more companies to the comparison by adding more `company_ids` parameters.

#### 6. Delete a Company

To remove a company from the system:

```bash
curl -X DELETE http://localhost:8000/api/companies/company1
```

#### 7. Analyze a Company

To analyze a company using the DeepSeek API:

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech Innovations Inc.",
    "website": "https://techinnovations.example.com"
  }'
```

This will return a comprehensive description of the company.

#### 8. Find Comparable Companies

To find comparable public companies using the DeepSeek API:

```bash
curl -X POST http://localhost:8000/api/comparable \
  -H "Content-Type: application/json" \
  -d '{
    "company_description": "Tech Innovations Inc. is a leading technology company specializing in AI solutions...",
    "count": 10
  }'
```

This will return a list of comparable companies with their stock tickers and match rationales.

## Integrating with the Frontend

The API is designed to work with the Next.js frontend application. The CORS middleware is configured to allow requests from `http://localhost:3000`, which is the default port for Next.js development server.

To connect the frontend to this API:

1. Make sure both the backend and frontend servers are running
2. Use fetch or axios in your frontend code to make requests to the API endpoints

Example of fetching companies in React:

```javascript
const fetchCompanies = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/companies');
    const data = await response.json();
    setCompanies(data);
  } catch (error) {
    console.error('Error fetching companies:', error);
  }
};
```

## Extending the API

To add new features to the API:

1. Define new models in `models.py` if needed
2. Add new endpoints in `main.py`
3. Implement any required business logic
4. Update the documentation
5. Extend the DeepSeek API integration in `deepseek_api.py`

## Troubleshooting

- If you see a warning about `schema_extra` being renamed to `json_schema_extra`, this is due to Pydantic v2 changes and doesn't affect functionality
- If you encounter CORS errors from the frontend, make sure the frontend URL is correctly added to the `allow_origins` list in the CORS middleware setup
- For database-related errors, remember this example uses an in-memory mock database; in a production environment, you would want to use a real database
- If DeepSeek API calls fail, verify your API key in the `.env` file

## Next Steps

To enhance this API for production use, consider:

1. Adding authentication and authorization
2. Connecting to a real database (PostgreSQL, MongoDB, etc.)
3. Implementing more advanced validation
4. Adding pagination for large datasets
5. Setting up logging and monitoring
6. Deploying to a production environment
7. Implementing rate limiting for DeepSeek API calls
8. Adding caching for DeepSeek API responses