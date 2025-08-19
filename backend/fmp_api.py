import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List

# Load environment variables
load_dotenv()

class FMPAPI:
    """Client for interacting with the Financial Modeling Prep (FMP) API"""
    
    def __init__(self):
        self.api_key = os.getenv("FMP_API_KEY")
        self.api_url = "https://financialmodelingprep.com/api/v3"
        
        if not self.api_key:
            print("Warning: FMP API key not found. Financial metrics will not be available.")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the FMP API"""
        if not self.api_key:
            return {"error": "FMP API key not configured"}
        
        if params is None:
            params = {}
        
        params["apikey"] = self.api_key
        
        try:
            response = requests.get(
                f"{self.api_url}/{endpoint}",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"FMP API request failed: {str(e)}"}
    
    def get_company_profile(self, ticker: str) -> Dict[str, Any]:
        """Get company profile and key financial metrics"""
        return self._make_request(f"profile/{ticker}")
    
    def get_company_quote(self, ticker: str) -> Dict[str, Any]:
        """Get real-time stock quote"""
        return self._make_request(f"quote/{ticker}")
    
    def get_financial_ratios(self, ticker: str) -> Dict[str, Any]:
        """Get key financial ratios"""
        return self._make_request(f"ratios/{ticker}")
    
    def get_income_statement(self, ticker: str, period: str = "annual") -> Dict[str, Any]:
        """Get income statement data"""
        return self._make_request(f"income-statement/{ticker}", {"period": period})
    
    def get_balance_sheet(self, ticker: str, period: str = "annual") -> Dict[str, Any]:
        """Get balance sheet data"""
        return self._make_request(f"balance-sheet-statement/{ticker}", {"period": period})
    
    def get_cash_flow(self, ticker: str, period: str = "annual") -> Dict[str, Any]:
        """Get cash flow statement data"""
        return self._make_request(f"cash-flow-statement/{ticker}", {"period": period})
    
    def get_key_metrics(self, ticker: str) -> Dict[str, Any]:
        """Get key financial metrics for a company"""
        try:
            # Get company profile
            profile = self.get_company_profile(ticker)
            if isinstance(profile, list) and len(profile) > 0:
                profile = profile[0]
            
            # Get quote data
            quote = self.get_company_quote(ticker)
            if isinstance(quote, list) and len(quote) > 0:
                quote = quote[0]
            
            # Extract key metrics
            metrics = {
                "ticker": ticker,
                "company_name": profile.get("companyName", "Unknown"),
                "market_cap": profile.get("mktCap", "N/A"),
                "enterprise_value": profile.get("enterpriseValue", "N/A"),
                "revenue": profile.get("revenue", "N/A"),
                "ebitda": profile.get("ebitda", "N/A"),
                "net_income": profile.get("netIncome", "N/A"),
                "current_price": quote.get("price", "N/A"),
                "currency": "USD"
            }
            
            return metrics
            
        except Exception as e:
            return {
                "ticker": ticker,
                "error": f"Failed to get metrics: {str(e)}",
                "note": "FMP API integration required for financial data"
            }
    
    def get_comparables_financials(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """Get financial metrics for multiple comparable companies"""
        results = []
        
        for ticker in tickers:
            metrics = self.get_key_metrics(ticker)
            results.append(metrics)
        
        return results 