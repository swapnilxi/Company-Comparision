from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any, Optional
from models import (
    CompanyAnalysisRequest, CompanyAnalysisResponse, 
    ComparableCompaniesRequest, ComparableCompaniesResponse
)
from deepseek_api import DeepSeekAPI
from fmp_api import FMPAPI

# Initialize router
router = APIRouter(prefix="/api", tags=["analysis"])

# Initialize API clients
deepseek_client = DeepSeekAPI()
fmp_client = FMPAPI()

def apply_filters_to_companies(companies: List[Dict[str, Any]], filters: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """
    Apply filters to comparable companies based on their characteristics.
    This is a simplified implementation - in a real app, you would have more detailed company data.
    """
    if not filters or not any(filters.values()):
        return companies
    
    filtered_companies = []
    
    for company in companies:
        # Get company profile data to apply filters
        try:
            profile = fmp_client.get_company_profile(company.get("ticker", ""))
            if isinstance(profile, list) and len(profile) > 0:
                profile = profile[0]
            
            if not isinstance(profile, dict) or profile.get("error"):
                # If we can't get profile data, include the company anyway
                filtered_companies.append(company)
                continue
            
            # Apply company size filter
            if filters.get("company_size"):
                market_cap = profile.get("mktCap", 0)
                size_matches = False
                
                for size_filter in filters["company_size"]:
                    if size_filter == "small" and market_cap < 2000000000:  # < $2B
                        size_matches = True
                    elif size_filter == "mid" and 2000000000 <= market_cap < 10000000000:  # $2B - $10B
                        size_matches = True
                    elif size_filter == "large" and 10000000000 <= market_cap < 100000000000:  # $10B - $100B
                        size_matches = True
                    elif size_filter == "mega" and market_cap >= 100000000000:  # >= $100B
                        size_matches = True
                
                if not size_matches:
                    continue
            
            # Apply geography filter (simplified - would need more data in real app)
            if filters.get("geography"):
                # For now, assume US companies if we have a ticker
                # In a real app, you'd have geographic data
                if "us" in filters["geography"] and company.get("ticker"):
                    pass  # Include US companies
                elif "us" not in filters["geography"]:
                    continue  # Skip if not US and US not in filters
            
            # Apply business characteristics filter (simplified)
            if filters.get("business_characteristics"):
                # This would require more detailed company analysis
                # For now, include all companies
                pass
            
            # Apply industry sectors filter (simplified)
            if filters.get("industry_sectors"):
                # This would require more detailed company analysis
                # For now, include all companies
                pass
            
            filtered_companies.append(company)
            
        except Exception:
            # If there's an error getting profile data, include the company anyway
            filtered_companies.append(company)
    
    return filtered_companies

@router.post("/find-comparables")
async def find_comparables_from_input(
    company_id: Optional[str] = Body(None, embed=True, description="Company ID from database"),
    company_name: Optional[str] = Body(None, embed=True, description="Company name"),
    company_website: Optional[str] = Body(None, embed=True, description="Company website URL"),
    ticker: Optional[str] = Body(None, embed=True, description="Public market ticker symbol"),
    count: int = Body(10, embed=True, description="Number of comparable companies to find", ge=1, le=20),
    filters: Dict[str, List[str]] = Body({}, embed=True, description="Filters for company characteristics")
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
            from database import get_company
            company = get_company(company_id)
            if not company:
                raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
            
            target_company_name = company.name
            target_company_website = f"https://{company.name.lower().replace(' ', '')}.com"  # Placeholder
            company_description = company.description or f"{company.name} is a {company.industry} company founded in {company.founded_year}."
        
        # Case 2: Ticker provided - fetch profile via FMP
        elif ticker:
            profile = fmp_client.get_company_profile(ticker)
            if isinstance(profile, list) and len(profile) > 0:
                profile = profile[0]
            if isinstance(profile, dict) and profile.get("error"):
                raise HTTPException(status_code=502, detail=profile["error"]) 

            target_company_name = profile.get("companyName") or ticker
            target_company_website = profile.get("website")
            if target_company_website and not target_company_website.startswith("http"):
                target_company_website = f"https://{target_company_website}"

            analysis_result = deepseek_client.analyze_company(
                company_name=target_company_name,
                company_website=target_company_website or f"https://{(target_company_name or '').lower().replace(' ', '')}.com"
            )
            company_description = analysis_result.get("description", "")

        # Case 3: Company name and website provided
        elif company_name and company_website:
            target_company_name = company_name
            target_company_website = company_website
            
            # Analyze the company using DeepSeek API
            analysis_result = deepseek_client.analyze_company(
                company_name=company_name,
                company_website=company_website
            )
            company_description = analysis_result.get("description", "")
        
        # Case 4: Only company name provided
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
        
        # Case 5: Only company website provided
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
        
        # Apply filters if provided
        if filters and any(filters.values()):
            comparable_companies = apply_filters_to_companies(comparable_companies, filters)
        
        # Return combined result
        return {
            "target_company": {
                "id": company_id,
                "name": target_company_name,
                "website": target_company_website,
                "description": company_description
            },
            "comparable_companies": comparable_companies,
            "filters_applied": filters,
            "analysis_timestamp": "2024-01-01T00:00:00Z",  # In real app, use actual timestamp
            "input_type": "company_id" if company_id else (
                "ticker" if ticker else (
                    "name_and_website" if company_name and company_website else (
                        "name_only" if company_name else "website_only"
                    )
                )
            )
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@router.post("/analyze", response_model=CompanyAnalysisResponse)
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

@router.post("/comparable", response_model=ComparableCompaniesResponse)
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

@router.post("/comparables-with-financials")
async def find_comparables_with_financials(
    company_id: Optional[str] = Body(None, embed=True, description="(Ignored) Company ID from database"),
    company_name: Optional[str] = Body(None, embed=True, description="Company name"),
    company_website: Optional[str] = Body(None, embed=True, description="Company website URL"),
    ticker: Optional[str] = Body(None, embed=True, description="Public market ticker symbol"),
    include_financials: bool = Body(True, embed=True, description="Whether to include financial metrics"),
    count: int = Body(10, embed=True, description="Number of comparable companies to find", ge=1, le=20)
):
    """
    Extension 1: Find comparable companies with financial metrics integration.
    
    This endpoint accepts flexible input (Database is NOT used):
    - company_name: Analyze company by name (works with or without website)
    - company_website: Analyze company by website (works with or without name)
    
    This endpoint includes:
    - Company analysis and comparable identification using DeepSeek API
    - Financial metrics (market cap, EBITDA, revenue) for each comparable company via FMP API
    """
    try:
        target_company_name = None
        target_company_website = None
        company_description = ""
        
        # Case 1: Ticker provided - fetch profile via FMP, then analyze
        if ticker:
            profile = fmp_client.get_company_profile(ticker)
            if isinstance(profile, list) and len(profile) > 0:
                profile = profile[0]
            if isinstance(profile, dict) and profile.get("error"):
                raise HTTPException(status_code=502, detail=profile["error"]) 

            target_company_name = profile.get("companyName") or ticker
            target_company_website = profile.get("website")
            if target_company_website and not target_company_website.startswith("http"):
                target_company_website = f"https://{target_company_website}"

            analysis_result = deepseek_client.analyze_company(
                company_name=target_company_name,
                company_website=target_company_website or f"https://{(target_company_name or '').lower().replace(' ', '')}.com"
            )
            company_description = analysis_result.get("description", "")

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
            raise HTTPException(status_code=400, detail="At least one of ticker, company_name or company_website must be provided")
        
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
                "id": None,
                "name": target_company_name,
                "website": target_company_website,
                "description": company_description
            },
            "comparable_companies": comparable_companies,
            "financial_data_included": include_financials,
            "note": "Financial metrics provided by FMP API integration",
            "input_type": "ticker" if ticker else ("name_and_website" if company_name and company_website else ("name_only" if company_name else "website_only"))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@router.post("/refine-comparables")
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

@router.get("/refinement-suggestions")
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

@router.post("/detailed-comparison")
async def get_detailed_comparison(
    tickers: List[str] = Body(..., description="List of ticker symbols to compare"),
    include_ratios: bool = Body(True, description="Include financial ratios"),
    include_statements: bool = Body(False, description="Include financial statements"),
    filters: Dict[str, Any] = Body({}, description="Filters for company characteristics")
):
    """
    Get detailed financial comparison data for multiple companies.
    
    This endpoint provides comprehensive financial data for comparison including:
    - Company profiles and basic metrics
    - Financial ratios (P/E, P/B, ROE, etc.)
    - Financial statements (if requested)
    - Market data and valuation metrics
    """
    try:
        if not tickers:
            raise HTTPException(status_code=400, detail="At least one ticker must be provided")
        
        if len(tickers) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 tickers allowed for comparison")
        
        comparison_data = []
        
        for ticker in tickers:
            ticker_data = {
                "ticker": ticker,
                "profile": None,
                "quote": None,
                "ratios": None,
                "statements": None
            }
            
            # Get company profile
            profile = fmp_client.get_company_profile(ticker)
            if isinstance(profile, list) and len(profile) > 0:
                profile = profile[0]
            if not isinstance(profile, dict) or profile.get("error"):
                ticker_data["error"] = profile.get("error", "Failed to fetch profile")
            else:
                ticker_data["profile"] = profile
            
            # Get quote data
            quote = fmp_client.get_company_quote(ticker)
            if isinstance(quote, list) and len(quote) > 0:
                quote = quote[0]
            if not isinstance(quote, dict) or quote.get("error"):
                ticker_data["quote_error"] = quote.get("error", "Failed to fetch quote")
            else:
                ticker_data["quote"] = quote
            
            # Get financial ratios if requested
            if include_ratios:
                ratios = fmp_client.get_financial_ratios(ticker)
                if isinstance(ratios, list) and len(ratios) > 0:
                    ratios = ratios[0]  # Get most recent
                if not isinstance(ratios, dict) or ratios.get("error"):
                    ticker_data["ratios_error"] = ratios.get("error", "Failed to fetch ratios")
                else:
                    ticker_data["ratios"] = ratios
            
            # Get financial statements if requested
            if include_statements:
                statements = {
                    "income": fmp_client.get_income_statement(ticker),
                    "balance": fmp_client.get_balance_sheet(ticker),
                    "cash_flow": fmp_client.get_cash_flow(ticker)
                }
                ticker_data["statements"] = statements
            
            comparison_data.append(ticker_data)
        
        return {
            "tickers": tickers,
            "comparison_data": comparison_data,
            "include_ratios": include_ratios,
            "include_statements": include_statements,
            "filters_applied": filters,
            "timestamp": "2024-01-01T00:00:00Z"  # In real app, use actual timestamp
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting detailed comparison: {str(e)}")

@router.post("/company-details")
async def get_company_details(
    ticker: str = Body(..., description="Ticker symbol of the company"),
    include_financials: bool = Body(True, description="Include financial metrics"),
    include_ratios: bool = Body(True, description="Include financial ratios")
):
    """
    Get detailed information for a single company including financial metrics and ratios.
    """
    try:
        company_data = {
            "ticker": ticker,
            "profile": None,
            "quote": None,
            "ratios": None,
            "financials": None
        }
        
        # Get company profile
        profile = fmp_client.get_company_profile(ticker)
        if isinstance(profile, list) and len(profile) > 0:
            profile = profile[0]
        if not isinstance(profile, dict) or profile.get("error"):
            company_data["error"] = profile.get("error", "Failed to fetch profile")
        else:
            company_data["profile"] = profile
        
        # Get quote data
        quote = fmp_client.get_company_quote(ticker)
        if isinstance(quote, list) and len(quote) > 0:
            quote = quote[0]
        if not isinstance(quote, dict) or quote.get("error"):
            company_data["quote_error"] = quote.get("error", "Failed to fetch quote")
        else:
            company_data["quote"] = quote
        
        # Get financial ratios if requested
        if include_ratios:
            ratios = fmp_client.get_financial_ratios(ticker)
            if isinstance(ratios, list) and len(ratios) > 0:
                ratios = ratios[0]  # Get most recent
            if not isinstance(ratios, dict) or ratios.get("error"):
                company_data["ratios_error"] = ratios.get("error", "Failed to fetch ratios")
            else:
                company_data["ratios"] = ratios
        
        # Get additional financial data if requested
        if include_financials:
            # Get income statement for additional metrics
            income = fmp_client.get_income_statement(ticker)
            if isinstance(income, list) and len(income) > 0:
                income = income[0]  # Get most recent
            if not isinstance(income, dict) or income.get("error"):
                company_data["financials_error"] = income.get("error", "Failed to fetch financials")
            else:
                company_data["financials"] = income
        
        return company_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting company details: {str(e)}")

@router.get("/filter-options")
async def get_filter_options():
    """
    Get available filter options for company characteristics
    """
    return {
        "company_size": [
            {"value": "small", "label": "Small Cap (< $2B)"},
            {"value": "mid", "label": "Mid Cap ($2B - $10B)"},
            {"value": "large", "label": "Large Cap (> $10B)"},
            {"value": "mega", "label": "Mega Cap (> $100B)"}
        ],
        "geography": [
            {"value": "us", "label": "United States"},
            {"value": "europe", "label": "Europe"},
            {"value": "asia", "label": "Asia"},
            {"value": "global", "label": "Global"}
        ],
        "business_characteristics": [
            {"value": "saas", "label": "SaaS/Software"},
            {"value": "ecommerce", "label": "E-commerce"},
            {"value": "marketplace", "label": "Marketplace"},
            {"value": "subscription", "label": "Subscription Model"},
            {"value": "b2b", "label": "B2B"},
            {"value": "b2c", "label": "B2C"},
            {"value": "fintech", "label": "Fintech"},
            {"value": "healthtech", "label": "Health Tech"},
            {"value": "ai_ml", "label": "AI/ML"},
            {"value": "enterprise", "label": "Enterprise Software"}
        ],
        "industry_sectors": [
            {"value": "technology", "label": "Technology"},
            {"value": "healthcare", "label": "Healthcare"},
            {"value": "finance", "label": "Financial Services"},
            {"value": "retail", "label": "Retail"},
            {"value": "manufacturing", "label": "Manufacturing"},
            {"value": "energy", "label": "Energy"},
            {"value": "telecommunications", "label": "Telecommunications"},
            {"value": "consumer_goods", "label": "Consumer Goods"}
        ]
    }



