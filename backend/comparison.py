from typing import Dict, List, Tuple
from models import Company, ComparisonResult


def compare_companies(companies: List[Company]) -> ComparisonResult:
    """Compare multiple companies and generate a comparison result"""
    if len(companies) < 2:
        raise ValueError("At least two companies are required for comparison")
    
    # Extract company IDs
    company_ids = [company.id for company in companies]
    
    # Create metrics dictionary
    metrics = {}
    for company in companies:
        metrics[company.id] = {
            "revenue": company.financial_data.revenue,
            "profit_margin": company.financial_data.profit_margin,
            "growth_rate": company.financial_data.growth_rate,
            "market_share": company.financial_data.market_share or 0  # Default to 0 if None
        }
    
    # Generate comparison summary
    summary = generate_comparison_summary(companies)
    
    # Create and return comparison result
    return ComparisonResult(
        companies=company_ids,
        metrics=metrics,
        summary=summary
    )


def generate_comparison_summary(companies: List[Company]) -> Dict[str, str]:
    """Generate a summary of the comparison between companies"""
    summary = {}
    
    # Compare revenue
    companies_by_revenue = sorted(companies, key=lambda c: c.financial_data.revenue, reverse=True)
    highest_revenue = companies_by_revenue[0]
    lowest_revenue = companies_by_revenue[-1]
    revenue_diff_percent = ((highest_revenue.financial_data.revenue - lowest_revenue.financial_data.revenue) / 
                           lowest_revenue.financial_data.revenue * 100)
    summary["revenue"] = f"{highest_revenue.name} has {revenue_diff_percent:.1f}% higher revenue than {lowest_revenue.name}"
    
    # Compare profit margin
    companies_by_profit = sorted(companies, key=lambda c: c.financial_data.profit_margin, reverse=True)
    highest_profit = companies_by_profit[0]
    lowest_profit = companies_by_profit[-1]
    profit_diff = highest_profit.financial_data.profit_margin - lowest_profit.financial_data.profit_margin
    summary["profit_margin"] = f"{highest_profit.name} has a {profit_diff:.1f}% higher profit margin than {lowest_profit.name}"
    
    # Compare growth rate
    companies_by_growth = sorted(companies, key=lambda c: c.financial_data.growth_rate, reverse=True)
    highest_growth = companies_by_growth[0]
    lowest_growth = companies_by_growth[-1]
    growth_diff = highest_growth.financial_data.growth_rate - lowest_growth.financial_data.growth_rate
    summary["growth_rate"] = f"{highest_growth.name} has a {growth_diff:.1f}% higher growth rate than {lowest_growth.name}"
    
    # Compare market share
    companies_with_market_share = [c for c in companies if c.financial_data.market_share is not None]
    if companies_with_market_share:
        companies_by_market = sorted(companies_with_market_share, key=lambda c: c.financial_data.market_share, reverse=True)
        highest_market = companies_by_market[0]
        lowest_market = companies_by_market[-1]
        market_diff = highest_market.financial_data.market_share - lowest_market.financial_data.market_share
        summary["market_share"] = f"{highest_market.name} has a {market_diff:.1f}% higher market share than {lowest_market.name}"
    else:
        summary["market_share"] = "Market share data not available for comparison"
    
    # Add industry comparison if companies are from different industries
    industries = set(company.industry for company in companies)
    if len(industries) > 1:
        summary["industry"] = f"Companies operate in different industries: {', '.join(industries)}"
    
    return summary