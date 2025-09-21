#!/usr/bin/env python3
"""
Test script for the RAG service
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_service import RAGService

def test_rag_service():
    """Test the RAG service with sample data"""
    
    # Initialize RAG service
    rag = RAGService()
    
    # Sample comparison data
    sample_data = {
        "target_company": {
            "name": "TechCorp Inc",
            "description": "A leading technology company specializing in cloud computing and AI solutions",
            "industry": "Technology",
            "business_model": "SaaS",
            "company_size": "Large",
            "geographic_presence": "Global"
        },
        "comparable_companies": [
            {
                "name": "CloudTech Solutions",
                "ticker": "CLDT",
                "rationale": "Similar cloud computing focus and enterprise customer base",
                "industry": "Technology",
                "business_model": "SaaS",
                "company_size": "Medium",
                "financial_metrics": {
                    "market_cap": 5000000000,
                    "pe_ratio": 18.5,
                    "roe": 12.3,
                    "net_margin": 15.2
                }
            },
            {
                "name": "AI Innovations Ltd",
                "ticker": "AIIL",
                "rationale": "AI-focused technology company with similar market positioning",
                "industry": "Technology",
                "business_model": "Product + Services",
                "company_size": "Medium",
                "financial_metrics": {
                    "market_cap": 3200000000,
                    "pe_ratio": 22.1,
                    "roe": 8.7,
                    "net_margin": 12.8
                }
            }
        ],
        "analysis_timestamp": "2024-01-15T10:00:00Z"
    }
    
    print("Testing RAG Service...")
    print("=" * 50)
    
    # Test context setting
    print("1. Setting comparison context...")
    rag.set_comparison_context(sample_data)
    print("✓ Context set successfully")
    
    # Test context info
    print("\n2. Getting context info...")
    context_info = rag.get_context_info()
    print(f"✓ Context info: {context_info}")
    
    # Test various queries
    test_queries = [
        "Give me a summary of the comparison",
        "Which companies have the best financial metrics?",
        "What are the key industry patterns?",
        "Compare the companies",
        "What investment insights can you provide?"
    ]
    
    print("\n3. Testing queries...")
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query}")
        print("-" * 40)
        response = rag.process_query(query)
        print(f"Response: {response}")
        print("-" * 40)
    
    # Test conversation history
    print("\n4. Testing conversation history...")
    history = rag.get_conversation_history()
    print(f"✓ Conversation turns: {len(history)}")
    
    # Test FAISS functionality (if available)
    if rag.sentence_model and rag.index:
        print("\n5. Testing FAISS search...")
        search_results = rag._search_similar_documents("cloud computing technology", top_k=2)
        print(f"✓ FAISS search results: {len(search_results)} documents found")
        for i, result in enumerate(search_results):
            print(f"  Result {i+1}: {result['text'][:100]}...")
    else:
        print("\n5. FAISS not available - skipping vector search test")
    
    print("\n" + "=" * 50)
    print("RAG Service test completed successfully!")
    
    return True

if __name__ == "__main__":
    try:
        test_rag_service()
    except Exception as e:
        print(f"Error testing RAG service: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

