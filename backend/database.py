from models import Company, FinancialMetric, CompanySize

# Mock database for storing company data
companies_db = {
    "company1": Company(
        id="company1",
        name="Tech Innovations Inc.",
        industry="Technology",
        size=CompanySize.LARGE,
        founded_year=2005,
        description="A leading technology company specializing in AI solutions",
        financial_data=FinancialMetric(
            revenue=5000000.0,
            profit_margin=15.5,
            growth_rate=8.2,
            market_share=12.3
        )
    ),
    "company2": Company(
        id="company2",
        name="Green Energy Solutions",
        industry="Renewable Energy",
        size=CompanySize.MEDIUM,
        founded_year=2010,
        description="Innovative renewable energy solutions provider",
        financial_data=FinancialMetric(
            revenue=2500000.0,
            profit_margin=12.8,
            growth_rate=15.3,
            market_share=7.5
        )
    ),
    "company3": Company(
        id="company3",
        name="HealthPlus Medical",
        industry="Healthcare",
        size=CompanySize.LARGE,
        founded_year=1998,
        description="Leading healthcare provider with innovative medical solutions",
        financial_data=FinancialMetric(
            revenue=8200000.0,
            profit_margin=18.2,
            growth_rate=6.7,
            market_share=22.1
        )
    ),
    "company4": Company(
        id="company4",
        name="FinTech Innovations",
        industry="Financial Services",
        size=CompanySize.SMALL,
        founded_year=2018,
        description="Cutting-edge financial technology startup",
        financial_data=FinancialMetric(
            revenue=800000.0,
            profit_margin=9.5,
            growth_rate=25.8,
            market_share=2.3
        )
    ),
}


# Database operations
def get_all_companies():
    """Get all companies from the database"""
    return list(companies_db.values())


def get_company(company_id: str):
    """Get a company by ID"""
    return companies_db.get(company_id)


def create_company(company_id: str, company: Company):
    """Create a new company"""
    companies_db[company_id] = company
    return company


def update_company(company_id: str, company_data: dict):
    """Update an existing company"""
    if company_id not in companies_db:
        return None
    
    current_company = companies_db[company_id]
    updated_company = current_company.copy(update=company_data)
    companies_db[company_id] = updated_company
    return updated_company


def delete_company(company_id: str):
    """Delete a company"""
    if company_id not in companies_db:
        return False
    
    del companies_db[company_id]
    return True