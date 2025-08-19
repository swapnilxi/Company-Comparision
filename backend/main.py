from fastapi import FastAPI, HTTPException, Path, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import uvicorn
import os
from dotenv import load_dotenv

# Import models and database
from models import (
    Company, CompanyCreate, ComparisonResult, 
    CompanyAnalysisRequest, CompanyAnalysisResponse, 
    ComparableCompaniesRequest, ComparableCompaniesResponse,
    ComparableCompany
)
import database as db
from comparison import compare_companies
from deepseek_api import DeepSeekAPI
from fmp_api import FMPAPI

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Company Comparison API",
    description="API for comparing company financial data and finding comparable companies",
    version="1.0.0"
)

# Initialize API clients
deepseek_client = DeepSeekAPI()
fmp_client = FMPAPI()

# Add CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Realtime market data endpoints (FMP)
@app.get("/api/market/quote/{ticker}", tags=["market"])
async def get_realtime_quote(ticker: str = Path(..., description="Stock ticker symbol, e.g., AAPL")):
    """Get real-time quote for a single ticker using FMP"""
    data = fmp_client.get_company_quote(ticker)
    # FMP returns a list for quote endpoints; normalize to single object when possible
    if isinstance(data, list):
        if not data:
            raise HTTPException(status_code=404, detail=f"Quote not found for {ticker}")
        data = data[0]
    if isinstance(data, dict) and data.get("error"):
        raise HTTPException(status_code=502, detail=data["error"]) 
    return data

@app.get("/api/market/price/{ticker}", tags=["market"])
async def get_realtime_price(ticker: str = Path(..., description="Stock ticker symbol, e.g., AAPL")):
    """Get lightweight real-time price for a single ticker using FMP"""
    data = fmp_client.get_realtime_price(ticker)
    if isinstance(data, list):
        if not data:
            raise HTTPException(status_code=404, detail=f"Price not found for {ticker}")
        data = data[0]
    if isinstance(data, dict) and data.get("error"):
        raise HTTPException(status_code=502, detail=data["error"]) 
    return data

@app.get("/api/market/quotes", tags=["market"])
async def get_realtime_quotes(tickers: List[str] = Query(..., description="Tickers as repeated params (?tickers=AAPL&tickers=MSFT) or a single comma-separated value")):
    """Get real-time quotes for multiple tickers using FMP"""
    # Support both repeated params and comma-separated inside a single item
    if isinstance(tickers, list) and len(tickers) == 1 and "," in tickers[0]:
        tickers = [t.strip() for t in tickers[0].split(",") if t.strip()]
    data = fmp_client.get_realtime_prices(tickers)
    if isinstance(data, dict) and data.get("error"):
        raise HTTPException(status_code=502, detail=data["error"]) 
    if isinstance(tickers, list) and not data:
        raise HTTPException(status_code=404, detail="No quotes found for provided tickers")
    return data

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Company Comparison API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Get all companies
@app.get("/api/companies", response_model=List[Company], tags=["companies"])
async def get_companies():
    """Get all companies"""
    return db.get_all_companies()

# Get a specific company by ID
@app.get("/api/companies/{company_id}", response_model=Company, tags=["companies"])
async def get_company(company_id: str = Path(..., description="The ID of the company to retrieve")):
    """Get a specific company by ID"""
    company = db.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
    return company

# Create a new company
@app.post("/api/companies", response_model=Company, status_code=201, tags=["companies"])
async def create_company(company: CompanyCreate):
    """Create a new company"""
    # Generate a simple ID based on the company name
    company_id = company.name.lower().replace(" ", "_")[:10] + "_" + str(len(db.get_all_companies()) + 1)
    
    # Check if company with this ID already exists
    if db.get_company(company_id):
        raise HTTPException(status_code=400, detail=f"Company with ID {company_id} already exists")
    
    # Create new company object
    new_company = Company(
        id=company_id,
        **company.dict()
    )
    
    # Add to database
    return db.create_company(company_id, new_company)

# Update a company
@app.put("/api/companies/{company_id}", response_model=Company, tags=["companies"])
async def update_company(
    company_data: Dict[str, Any],
    company_id: str = Path(..., description="The ID of the company to update")
):
    """Update a company"""
    updated_company = db.update_company(company_id, company_data)
    if not updated_company:
        raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
    return updated_company

# Delete a company
@app.delete("/api/companies/{company_id}", tags=["companies"])
async def delete_company(company_id: str = Path(..., description="The ID of the company to delete")):
    """Delete a company"""
    success = db.delete_company(company_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
    return {"message": f"Company with ID {company_id} deleted successfully"}

# Compare companies
@app.get("/api/compare", response_model=ComparisonResult, tags=["comparison"])
async def compare(
    company_ids: List[str] = Query(..., description="List of company IDs to compare")
):
    """Compare multiple companies"""
    # Check if we have at least 2 companies to compare
    if len(company_ids) < 2:
        raise HTTPException(status_code=400, detail="At least two companies are required for comparison")
    
    # Get companies from database
    companies = []
    for company_id in company_ids:
        company = db.get_company(company_id)
        if not company:
            raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
        companies.append(company)
    
    # Generate comparison
    try:
        comparison_result = compare_companies(companies)
        return comparison_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing companies: {str(e)}")

# Company Analysis endpoint
@app.post("/api/analyze", response_model=CompanyAnalysisResponse, tags=["analysis"])
async def analyze_company(request: CompanyAnalysisRequest):
    """Analyze a company based on name and website"""
    try:
        # Call DeepSeek API to analyze the company and return structured output
        analysis_result = deepseek_client.analyze_company(
            company_name=request.name,
            company_website=str(request.website)
        )

        return CompanyAnalysisResponse(
            name=request.name,
            website=str(request.website),
            description=analysis_result.get("description", ""),
            industry=analysis_result.get("industry"),
            business_model=analysis_result.get("business_model"),
            products_or_services=analysis_result.get("products_or_services"),
            target_market=analysis_result.get("target_market"),
            company_size=analysis_result.get("company_size"),
            geographic_presence=analysis_result.get("geographic_presence"),
            key_differentiators=analysis_result.get("key_differentiators")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing company: {str(e)}")

# Find comparable companies endpoint
@app.post("/api/comparable", response_model=ComparableCompaniesResponse, tags=["analysis"])
async def find_comparable_companies(request: ComparableCompaniesRequest):
    """Find comparable public companies based on a company description"""
    try:
        # Extract target company name from the description
        # This is a simple implementation - in a real app, you might want to use
        # more sophisticated techniques
        target_company = "Unknown Company"
        if "name:" in request.company_description.lower():
            name_start = request.company_description.lower().find("name:") + len("name:")
            name_end = request.company_description.find("\n", name_start)
            if name_end == -1:
                name_end = len(request.company_description)
            target_company = request.company_description[name_start:name_end].strip()
        
        # Call DeepSeek API to find comparable companies
        comparable_companies = deepseek_client.find_comparable_companies(
            company_description=request.company_description,
            count=request.count
        )
        
        return ComparableCompaniesResponse(
            target_company=target_company,
            comparable_companies=comparable_companies
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding comparable companies: {str(e)}")

# NEW: Combined endpoint for company analysis and comparable companies (Core Requirements)
@app.post("/api/find-comparables", tags=["analysis"])
async def find_comparables_from_input(
    company_id: Optional[str] = Body(None, embed=True, description="Company ID from database"),
    company_name: Optional[str] = Body(None, embed=True, description="Company name"),
    company_website: Optional[str] = Body(None, embed=True, description="Company website URL"),
    count: int = Body(10, embed=True, description="Number of comparable companies to find", ge=1, le=20)
):
    """
    Main endpoint that takes company information and finds comparable public companies.
    
    This endpoint accepts flexible input:
    - company_id: Use existing company from database
    - company_name: Analyze company by name (requires website)
    - company_website: Analyze company by website (requires name)
    
    This endpoint implements the core requirements from the README:
    - Input: Company ID, name, or website
    - Analysis: Generate comprehensive company description
    - Output: 7-10 comparable public companies with name, ticker, and rationale
    """
    try:
        target_company_name = None
        target_company_website = None
        company_description = ""
        
        # Case 1: Company ID provided - get from database
        if company_id:
            company = db.get_company(company_id)
            if not company:
                raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
            
            target_company_name = company.name
            target_company_website = f"https://{company.name.lower().replace(' ', '')}.com"  # Placeholder
            company_description = company.description or f"{company.name} is a {company.industry} company founded in {company.founded_year}."
        
        # Case 2: Company name and website provided
        elif company_name and company_website:
            target_company_name = company_name
            target_company_website = company_website
            
            # Analyze the company using DeepSeek API
            analysis_result = deepseek_client.analyze_company(
                company_name=company_name,
                company_website=company_website
            )
            company_description = analysis_result.get("description", "")
        
        # Case 3: Only company name provided
        elif company_name:
            target_company_name = company_name
            target_company_website = f"https://{company_name.lower().replace(' ', '')}.com"  # Placeholder
            
            # Try to analyze with placeholder website
            try:
                analysis_result = deepseek_client.analyze_company(
                    company_name=company_name,
                    company_website=target_company_website
                )
                company_description = analysis_result.get("description", "")
            except:
                # Fallback to basic description
                company_description = f"{company_name} is a company that we're analyzing for comparable companies."
        
        # Case 4: Only company website provided
        elif company_website:
            # Extract company name from website
            from urllib.parse import urlparse
            parsed_url = urlparse(company_website)
            target_company_name = parsed_url.netloc.replace('www.', '').split('.')[0].title()
            target_company_website = company_website
            
            # Try to analyze with extracted name
            try:
                analysis_result = deepseek_client.analyze_company(
                    company_name=target_company_name,
                    company_website=company_website
                )
                company_description = analysis_result.get("description", "")
            except:
                # Fallback to basic description
                company_description = f"{target_company_name} is a company with website {company_website} that we're analyzing for comparable companies."
        
        else:
            raise HTTPException(status_code=400, detail="At least one of company_id, company_name, or company_website must be provided")
        
        # Find comparable companies
        comparable_companies = deepseek_client.find_comparable_companies(
            company_description=company_description,
            count=count
        )
        
        # Return combined result
        return {
            "target_company": {
                "id": company_id,
                "name": target_company_name,
                "website": target_company_website,
                "description": company_description
            },
            "comparable_companies": comparable_companies,
            "analysis_timestamp": "2024-01-01T00:00:00Z",  # In real app, use actual timestamp
            "input_type": "company_id" if company_id else "name_and_website" if company_name and company_website else "name_only" if company_name else "website_only"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# NEW: Financial Metrics Integration (Extension 1)
@app.post("/api/comparables-with-financials", tags=["analysis", "financials"])
async def find_comparables_with_financials(
    company_id: Optional[str] = Body(None, embed=True, description="Company ID from database"),
    company_name: Optional[str] = Body(None, embed=True, description="Company name"),
    company_website: Optional[str] = Body(None, embed=True, description="Company website URL"),
    include_financials: bool = Body(True, embed=True, description="Whether to include financial metrics"),
    count: int = Body(10, embed=True, description="Number of comparable companies to find", ge=1, le=20)
):
    """
    Extension 1: Find comparable companies with financial metrics integration.
    
    This endpoint accepts flexible input:
    - company_id: Use existing company from database
    - company_name: Analyze company by name (works with or without website)
    - company_website: Analyze company by website (works with or without name)
    
    This endpoint includes:
    - Company analysis and comparable identification
    - Financial metrics (market cap, EBITDA, revenue) for each comparable company
    - Integration with FMP API for real financial data
    """
    try:
        target_company_name = None
        target_company_website = None
        company_description = ""
        
        # Case 1: Company ID provided - get from database
        if company_id:
            company = db.get_company(company_id)
            if not company:
                raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
            
            target_company_name = company.name
            target_company_website = f"https://{company.name.lower().replace(' ', '')}.com"  # Placeholder
            company_description = company.description or f"{company.name} is a {company.industry} company founded in {company.founded_year}."
        
        # Case 2: Company name and website provided
        elif company_name and company_website:
            target_company_name = company_name
            target_company_website = company_website
            
            # Analyze the company using DeepSeek API
            analysis_result = deepseek_client.analyze_company(
                company_name=company_name,
                company_website=company_website
            )
            company_description = analysis_result.get("description", "")
        
        # Case 3: Only company name provided
        elif company_name:
            target_company_name = company_name
            target_company_website = f"https://{company_name.lower().replace(' ', '')}.com"  # Placeholder
            
            # Try to analyze with placeholder website
            try:
                analysis_result = deepseek_client.analyze_company(
                    company_name=company_name,
                    company_website=target_company_website
                )
                company_description = analysis_result.get("description", "")
            except:
                # Fallback to basic description
                company_description = f"{company_name} is a company that we're analyzing for comparable companies."
        
        # Case 4: Only company website provided
        elif company_website:
            # Extract company name from website
            from urllib.parse import urlparse
            parsed_url = urlparse(company_website)
            target_company_name = parsed_url.netloc.replace('www.', '').split('.')[0].title()
            target_company_website = company_website
            
            # Try to analyze with extracted name
            try:
                analysis_result = deepseek_client.analyze_company(
                    company_name=target_company_name,
                    company_website=company_website
                )
                company_description = analysis_result.get("description", "")
            except:
                # Fallback to basic description
                company_description = f"{target_company_name} is a company with website {company_website} that we're analyzing for comparable companies."
        
        else:
            raise HTTPException(status_code=400, detail="At least one of company_id, company_name, or company_website must be provided")
        
        # Find comparable companies
        comparable_companies = deepseek_client.find_comparable_companies(
            company_description=company_description,
            count=count
        )
        
        # Add financial metrics if requested
        if include_financials:
            # Extract ticker symbols from comparable companies
            tickers = []
            for company in comparable_companies:
                if isinstance(company, dict) and "ticker" in company:
                    tickers.append(company["ticker"])
            
            # Get financial data from FMP API
            if tickers:
                financial_data = fmp_client.get_comparables_financials(tickers)
                
                # Create a mapping of ticker to financial data
                financial_map = {}
                for data in financial_data:
                    if "ticker" in data:
                        financial_map[data["ticker"]] = data
                
                # Add financial metrics to comparable companies
                for company in comparable_companies:
                    if isinstance(company, dict) and "ticker" in company:
                        ticker = company["ticker"]
                        if ticker in financial_map:
                            company["financial_metrics"] = financial_map[ticker]
                        else:
                            company["financial_metrics"] = {
                                "ticker": ticker,
                                "error": "Financial data not available",
                                "note": "FMP API integration required"
                            }
        
        return {
            "target_company": {
                "id": company_id,
                "name": target_company_name,
                "website": target_company_website,
                "description": company_description
            },
            "comparable_companies": comparable_companies,
            "financial_data_included": include_financials,
            "note": "Financial metrics provided by FMP API integration",
            "input_type": "company_id" if company_id else "name_and_website" if company_name and company_website else "name_only" if company_name else "website_only"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# NEW: Interactive Refinement (Extension 2)
@app.post("/api/refine-comparables", tags=["analysis", "refinement"])
async def refine_comparable_search(
    original_request: Dict[str, Any] = Body(..., description="Original search request"),
    user_feedback: str = Body(..., description="User feedback for refinement"),
    refinement_type: str = Body(..., description="Type of refinement: 'industry', 'size', 'geography', 'business_model'"),
    additional_count: int = Body(5, description="Additional companies to find based on feedback", ge=1, le=10)
):
    """
    Extension 2: Interactive refinement based on user feedback.
    
    This endpoint allows users to:
    - Provide feedback on initial results
    - Specify areas for improvement
    - Generate additional companies based on feedback
    - Filter by company size, geography, or business characteristics
    """
    try:
        # Extract original company description
        company_description = original_request.get("company_description", "")
        
        # Create refined prompt based on user feedback
        refinement_prompt = f"""
        Original company description: {company_description}
        
        User feedback: {user_feedback}
        Refinement type: {refinement_type}
        
        Please find {additional_count} additional comparable companies that address the user's feedback.
        Focus on the specific refinement area mentioned.
        """
        
        # Call DeepSeek API with refined prompt
        refined_companies = deepseek_client.find_comparable_companies(
            company_description=refinement_prompt,
            count=additional_count
        )
        
        return {
            "original_request": original_request,
            "user_feedback": user_feedback,
            "refinement_type": refinement_type,
            "additional_companies": refined_companies,
            "refinement_timestamp": "2024-01-01T00:00:00Z"  # In real app, use actual timestamp
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refining search: {str(e)}")

# NEW: Get refinement suggestions
@app.get("/api/refinement-suggestions", tags=["analysis", "refinement"])
async def get_refinement_suggestions():
    """
    Get available refinement options for interactive search
    """
    return {
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

# Run the application
if __name__ == "__main__":
    # Get host and port from environment variables or use defaults
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run("main:app", host=host, port=port, reload=debug)