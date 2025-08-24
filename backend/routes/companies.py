from fastapi import APIRouter, HTTPException, Path, Query
from typing import List, Dict, Any
from models import Company, CompanyCreate
import database as db

# Initialize router
router = APIRouter(prefix="/api/companies", tags=["companies"])

@router.get("/", response_model=List[Company])
async def get_companies():
    """Get all companies"""
    return db.get_all_companies()

@router.get("/{company_id}", response_model=Company)
async def get_company(company_id: str = Path(..., description="The ID of the company to retrieve")):
    """Get a specific company by ID"""
    company = db.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
    return company

@router.post("/", response_model=Company, status_code=201)
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

@router.put("/{company_id}", response_model=Company)
async def update_company(
    company_data: Dict[str, Any],
    company_id: str = Path(..., description="The ID of the company to update")
):
    """Update a company"""
    updated_company = db.update_company(company_id, company_data)
    if not updated_company:
        raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
    return updated_company

@router.delete("/{company_id}")
async def delete_company(company_id: str = Path(..., description="The ID of the company to delete")):
    """Delete a company"""
    success = db.delete_company(company_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
    return {"message": f"Company with ID {company_id} deleted successfully"}



