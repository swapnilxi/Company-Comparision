from fastapi import APIRouter, HTTPException, Query
from typing import List
from models import ComparisonResult
import database as db
from comparison import compare_companies

# Initialize router
router = APIRouter(prefix="/api", tags=["comparison"])

@router.get("/compare", response_model=ComparisonResult)
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



