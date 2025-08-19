import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test if the API is running"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_get_companies():
    """Test the companies endpoint"""
    response = requests.get(f"{BASE_URL}/api/companies")
    print(f"Get companies status: {response.status_code}")
    if response.status_code == 200:
        companies = response.json()
        print(f"Found {len(companies)} companies")
        return True
    return False

def test_analyze_company():
    """Test the company analysis endpoint"""
    payload = {
        "name": "Apple Inc.",
        "website": "https://www.apple.com"
    }
    response = requests.post(f"{BASE_URL}/api/analyze", json=payload)
    print(f"Analyze company status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("Analysis result:")
        print(f"Name: {result.get('name')}")
        print(f"Industry: {result.get('industry')}")
        print(f"Business model: {result.get('business_model')}")
        print(f"Description length: {len(result.get('description', ''))} characters")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_find_comparable_companies():
    """Test the comparable companies endpoint"""
    payload = {
        "company_description": "Apple Inc. is a technology company that designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories. The company also sells a variety of related services.",
        "count": 5
    }
    response = requests.post(f"{BASE_URL}/api/comparable", json=payload)
    print(f"Find comparable companies status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Target company: {result.get('target_company')}")
        companies = result.get('comparable_companies', [])
        print(f"Found {len(companies)} comparable companies:")
        for i, company in enumerate(companies):
            print(f"{i+1}. {company.get('name')} ({company.get('ticker')})")
        return True
    else:
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    print("Testing API endpoints...\n")
    
    print("1. Health Check")
    health_ok = test_api_health()
    print(f"Health check {'passed' if health_ok else 'failed'}\n")
    
    print("2. Get Companies")
    companies_ok = test_get_companies()
    print(f"Get companies {'passed' if companies_ok else 'failed'}\n")
    
    print("3. Analyze Company")
    analyze_ok = test_analyze_company()
    print(f"Analyze company {'passed' if analyze_ok else 'failed'}\n")
    
    print("4. Find Comparable Companies")
    comparable_ok = test_find_comparable_companies()
    print(f"Find comparable companies {'passed' if comparable_ok else 'failed'}\n")
    
    print("Summary:")
    all_passed = health_ok and companies_ok and analyze_ok and comparable_ok
    print(f"All tests {'passed' if all_passed else 'failed'}")