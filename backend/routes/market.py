from fastapi import APIRouter, HTTPException, Path, Query
from typing import List
from fmp_api import FMPAPI

# Initialize router
router = APIRouter(prefix="/api/market", tags=["market"])

# Initialize FMP client
fmp_client = FMPAPI()

@router.get("/quote/{ticker}")
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

@router.get("/price/{ticker}")
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

@router.get("/quotes")
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

@router.get("/profile/{ticker}")
async def get_company_profile(ticker: str = Path(..., description="Stock ticker symbol, e.g., AAPL")):
    """Get company profile (name, website, basic metrics) via FMP"""
    data = fmp_client.get_company_profile(ticker)
    if isinstance(data, list):
        data = data[0] if data else None
    if not data:
        raise HTTPException(status_code=404, detail=f"Profile not found for {ticker}")
    if isinstance(data, dict) and data.get("error"):
        raise HTTPException(status_code=502, detail=data["error"]) 
    return data



