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
        """Generate a comprehensive company description (structured) based on name and website"""
        prompt = f"""
        Generate a comprehensive business description for the following company and return a JSON object with these exact keys:
        - description: a detailed narrative summary
        - industry: primary industry or sector
        - business_model: concise description of how the company makes money
        - products_or_services: key products or services offered
        - target_market: primary customer segments or verticals
        - company_size: size/scale (employees, revenue band, or general descriptor)
        - geographic_presence: key regions/countries of operation
        - key_differentiators: brief list-style text of core differentiators

        Company Name: {company_name}
        Company Website: {company_website}
        """
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1200,
            "response_format": {"type": "json_object"}
        }
        
        response = self._make_request("chat/completions", payload)
        
        # Extract and parse the JSON content
        try:
            content = response["choices"][0]["message"]["content"]
            import json
            data = json.loads(content)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse DeepSeek API response: {e}")

        # Ensure required keys exist; provide safe defaults and normalize list values to strings
        def _to_string(value):
            if value is None:
                return None
            if isinstance(value, list):
                return ", ".join(str(item) for item in value)
            if isinstance(value, (dict,)):
                import json as _json
                return _json.dumps(value, ensure_ascii=False)
            return str(value)

        result = {
            "description": _to_string(data.get("description", "")),
            "industry": _to_string(data.get("industry")),
            "business_model": _to_string(data.get("business_model")),
            "products_or_services": _to_string(data.get("products_or_services")),
            "target_market": _to_string(data.get("target_market")),
            "company_size": _to_string(data.get("company_size")),
            "geographic_presence": _to_string(data.get("geographic_presence")),
            "key_differentiators": _to_string(data.get("key_differentiators"))
        }
        return result

    def analyze_company_with_feedback(self, company_name: str, company_website: str, feedback: str) -> Dict[str, Any]:
        """Generate or refine a company description using additional user feedback/context"""
        prompt = f"""
        Refine and update the comprehensive business description for the following company incorporating the user's feedback. Return a JSON object with these exact keys:
        - description: a detailed narrative summary (updated with user's feedback)
        - industry: primary industry or sector
        - business_model: concise description of how the company makes money
        - products_or_services: key products or services offered
        - target_market: primary customer segments or verticals
        - company_size: size/scale (employees, revenue band, or general descriptor)
        - geographic_presence: key regions/countries of operation
        - key_differentiators: brief list-style text of core differentiators

        Company Name: {company_name}
        Company Website: {company_website}

        User Feedback / Refinement Instructions:
        {feedback}
        """

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1200,
            "response_format": {"type": "json_object"}
        }

        response = self._make_request("chat/completions", payload)

        # Extract and parse JSON content
        try:
            content = response["choices"][0]["message"]["content"]
            import json
            data = json.loads(content)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse DeepSeek API response: {e}")

        def _to_string(value):
            if value is None:
                return None
            if isinstance(value, list):
                return ", ".join(str(item) for item in value)
            if isinstance(value, (dict,)):
                import json as _json
                return _json.dumps(value, ensure_ascii=False)
            return str(value)

        return {
            "description": _to_string(data.get("description", "")),
            "industry": _to_string(data.get("industry")),
            "business_model": _to_string(data.get("business_model")),
            "products_or_services": _to_string(data.get("products_or_services")),
            "target_market": _to_string(data.get("target_market")),
            "company_size": _to_string(data.get("company_size")),
            "geographic_presence": _to_string(data.get("geographic_presence")),
            "key_differentiators": _to_string(data.get("key_differentiators"))
        }
    
    def find_comparable_companies(self, company_description: str, count: int = 10) -> List[Dict[str, Any]]:
        """Find comparable public companies based on a company description"""
        prompt = f"""
        Based on the following company description, identify exactly {count} comparable public companies.

        Company Description:
        {company_description}

        Return a JSON object with a single key "companies" whose value is an array of objects.
        Each object must have these exact keys:
        - name: string (company name)
        - ticker: string (stock symbol, e.g., AAPL)
        - rationale: string (why this is comparable: industry, business model, size, market focus, etc.)
        """
        
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
            import json
            data = json.loads(content)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse DeepSeek API response: {e}")

        # Handle both object-with-companies and bare array formats
        if isinstance(data, dict):
            companies_raw = data.get("companies", [])
        elif isinstance(data, list):
            companies_raw = data
        else:
            companies_raw = []

        # Normalize fields and filter invalid entries
        normalized: List[Dict[str, Any]] = []
        for item in companies_raw:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("company") or item.get("company_name")
            ticker = item.get("ticker") or item.get("symbol")
            rationale = item.get("rationale") or item.get("reason") or item.get("match_rationale")
            if not name or not ticker:
                continue
            normalized.append({
                "name": str(name),
                "ticker": str(ticker),
                "rationale": str(rationale) if rationale is not None else ""
            })

        return normalized