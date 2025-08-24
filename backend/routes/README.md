# FastAPI Routes Structure

This directory contains the organized route files for the Company Comparison API, following FastAPI best practices for route organization.

## Route Organization

### `/routes/analysis.py`
Contains all analysis-related endpoints:
- `POST /api/find-comparables` - Main endpoint for finding comparable companies
- `POST /api/analyze` - Analyze a company based on name and website
- `POST /api/comparable` - Find comparable companies based on description
- `POST /api/comparables-with-financials` - Find comparables with financial metrics
- `POST /api/refine-comparables` - Interactive refinement based on user feedback
- `GET /api/refinement-suggestions` - Get available refinement options

### `/routes/companies.py`
Contains company CRUD operations:
- `GET /api/companies` - Get all companies
- `GET /api/companies/{company_id}` - Get a specific company
- `POST /api/companies` - Create a new company
- `PUT /api/companies/{company_id}` - Update a company
- `DELETE /api/companies/{company_id}` - Delete a company

### `/routes/comparison.py`
Contains comparison operations:
- `GET /api/compare` - Compare multiple companies

### `/routes/market.py`
Contains market data endpoints (FMP API integration):
- `GET /api/market/quote/{ticker}` - Get real-time quote for a ticker
- `GET /api/market/price/{ticker}` - Get real-time price for a ticker
- `GET /api/market/quotes` - Get real-time quotes for multiple tickers
- `GET /api/market/profile/{ticker}` - Get company profile

### `/routes/health.py`
Contains basic health and root endpoints:
- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

## Benefits of This Structure

1. **Modularity**: Each route file focuses on a specific domain
2. **Maintainability**: Easier to find and modify specific endpoints
3. **Scalability**: Easy to add new route files for new features
4. **Team Collaboration**: Different developers can work on different route files
5. **Testing**: Easier to write focused tests for specific route modules
6. **Documentation**: Clear separation of concerns makes API documentation more organized

## Usage

The routes are automatically included in the main FastAPI application via `app.include_router()` calls in `main.py`. Each router uses appropriate prefixes and tags for automatic API documentation generation.

## Adding New Routes

To add new routes:

1. Create a new route file in the `/routes` directory
2. Define your router with appropriate prefix and tags
3. Add your endpoint functions
4. Import and include the router in `main.py`

Example:
```python
# routes/new_feature.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/new-feature", tags=["new-feature"])

@router.get("/")
async def get_new_feature():
    return {"message": "New feature endpoint"}
```

Then in `main.py`:
```python
from routes import new_feature
app.include_router(new_feature.router)
```






