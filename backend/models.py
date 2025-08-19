from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, List, Optional, Any
from enum import Enum


class CompanySize(str, Enum):
    """Enum for company size categories"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class FinancialMetric(BaseModel):
    """Model for financial metrics"""
    revenue: float = Field(..., description="Annual revenue in USD")
    profit_margin: float = Field(..., description="Profit margin as a percentage")
    growth_rate: float = Field(..., description="Annual growth rate as a percentage")
    market_share: Optional[float] = Field(None, description="Market share as a percentage")


class CompanyBase(BaseModel):
    """Base model for company data"""
    name: str = Field(..., description="Company name")
    industry: str = Field(..., description="Industry sector")
    size: CompanySize = Field(..., description="Company size category")
    founded_year: int = Field(..., description="Year the company was founded")
    description: Optional[str] = Field(None, description="Brief company description")


class CompanyCreate(CompanyBase):
    """Model for creating a new company"""
    financial_data: FinancialMetric


class Company(CompanyBase):
    """Complete company model with ID"""
    id: str
    financial_data: FinancialMetric

    class Config:
        schema_extra = {
            "example": {
                "id": "company1",
                "name": "Tech Innovations Inc.",
                "industry": "Technology",
                "size": "large",
                "founded_year": 2005,
                "description": "A leading technology company specializing in AI solutions",
                "financial_data": {
                    "revenue": 5000000.0,
                    "profit_margin": 15.5,
                    "growth_rate": 8.2,
                    "market_share": 12.3
                }
            }
        }


class ComparisonResult(BaseModel):
    """Model for company comparison results"""
    companies: List[str] = Field(..., description="List of company IDs being compared")
    metrics: Dict[str, Dict[str, float]] = Field(..., description="Comparison metrics by company")
    summary: Dict[str, str] = Field(..., description="Summary of the comparison")

    class Config:
        schema_extra = {
            "example": {
                "companies": ["company1", "company2"],
                "metrics": {
                    "company1": {
                        "revenue": 5000000.0,
                        "profit_margin": 15.5,
                        "growth_rate": 8.2,
                        "market_share": 12.3
                    },
                    "company2": {
                        "revenue": 7500000.0,
                        "profit_margin": 18.2,
                        "growth_rate": 10.5,
                        "market_share": 15.7
                    }
                },
                "summary": {
                    "revenue": "Company2 has 50% higher revenue",
                    "profit_margin": "Company2 has a 2.7% higher profit margin",
                    "growth_rate": "Company2 has a 2.3% higher growth rate",
                    "market_share": "Company2 has a 3.4% higher market share"
                }
            }
        }


class CompanyAnalysisRequest(BaseModel):
    """Request model for company analysis"""
    name: str = Field(..., description="Company name")
    website: HttpUrl = Field(..., description="Company website URL")


class CompanyAnalysisResponse(BaseModel):
    """Response model for company analysis"""
    name: str = Field(..., description="Company name")
    website: str = Field(..., description="Company website URL")
    description: str = Field(..., description="Comprehensive company description")
    industry: Optional[str] = Field(None, description="Identified industry")
    business_model: Optional[str] = Field(None, description="Business model description")

    class Config:
        schema_extra = {
            "example": {
                "name": "Tech Innovations Inc.",
                "website": "https://techinnovations.example.com",
                "description": "Tech Innovations Inc. is a leading technology company specializing in AI solutions...",
                "industry": "Technology",
                "business_model": "SaaS (Software as a Service)"
            }
        }


class ComparableCompany(BaseModel):
    """Model for a comparable company"""
    name: str = Field(..., description="Company name")
    ticker: str = Field(..., description="Stock ticker symbol")
    rationale: str = Field(..., description="Explanation of why this company is comparable")


class ComparableCompaniesRequest(BaseModel):
    """Request model for finding comparable companies"""
    company_description: str = Field(..., description="Comprehensive company description")
    count: int = Field(10, description="Number of comparable companies to find", ge=1, le=20)


class ComparableCompaniesResponse(BaseModel):
    """Response model for comparable companies"""
    target_company: str = Field(..., description="Name of the target company")
    comparable_companies: List[ComparableCompany] = Field(..., description="List of comparable companies")

    class Config:
        schema_extra = {
            "example": {
                "target_company": "Tech Innovations Inc.",
                "comparable_companies": [
                    {
                        "name": "Microsoft Corporation",
                        "ticker": "MSFT",
                        "rationale": "Both companies focus on enterprise software solutions and AI technologies."
                    },
                    {
                        "name": "Salesforce, Inc.",
                        "ticker": "CRM",
                        "rationale": "Similar SaaS business model targeting enterprise customers."
                    }
                ]
            }
        }