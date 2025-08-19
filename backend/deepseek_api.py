import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Load environment variables
load_dotenv()

class DeepSeekAPI:
    """Client for interacting with the DeepSeek API"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")
        
        if not self.api_key:
            raise ValueError("DeepSeek API key not found. Please set DEEPSEEK_API_KEY in .env file.")
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{self.api_url}/{endpoint}",
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def analyze_company(self, company_name: str, company_website: str) -> Dict[str, Any]:
        """Generate a comprehensive company description based on name and website"""
        prompt = f"""Generate a comprehensive business description for the following company:
        Company Name: {company_name}
        Company Website: {company_website}
        
        Please include information about:
        1. Industry and sector
        2. Business model
        3. Products or services
        4. Target market and customers
        5. Company size and scale
        6. Geographic presence
        7. Key differentiators
        
        Format the response as a detailed business description."""
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        response = self._make_request("chat/completions", payload)
        
        # Extract the generated description from the response
        try:
            description = response["choices"][0]["message"]["content"]
            return {"description": description}
        except (KeyError, IndexError) as e:
            raise ValueError(f"Failed to parse DeepSeek API response: {e}")
    
    def find_comparable_companies(self, company_description: str, count: int = 10) -> List[Dict[str, Any]]:
        """Find comparable public companies based on a company description"""
        prompt = f"""Based on the following company description, identify {count} comparable public companies.
        
        Company Description:
        {company_description}
        
        For each comparable company, provide:
        1. Company Name
        2. Stock Ticker
        3. Match Rationale (why this company is comparable - industry, business model, size, market focus, etc.)
        
        Format the response as a JSON array with objects containing 'name', 'ticker', and 'rationale' fields."""
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
            "response_format": {"type": "json_object"}
        }
        
        response = self._make_request("chat/completions", payload)
        
        # Extract the generated comparable companies from the response
        try:
            content = response["choices"][0]["message"]["content"]
            # The content should be a JSON string that we need to parse
            import json
            comparable_companies = json.loads(content)
            return comparable_companies.get("companies", [])
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse DeepSeek API response: {e}")