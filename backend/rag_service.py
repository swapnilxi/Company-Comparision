import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle

class RAGService:
    """RAG (Retrieval-Augmented Generation) service for company comparison data"""
    
    def __init__(self):
        self.conversation_history = []
        self.current_context = {}
        
        # Initialize FAISS index and sentence transformer
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.dimension = 384  # Dimension of the sentence embeddings
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product index for cosine similarity
            self.documents = []  # Store document chunks
            self.document_metadata = []  # Store metadata for each chunk
        except Exception as e:
            print(f"Warning: Could not initialize FAISS/SentenceTransformer: {e}")
            self.sentence_model = None
            self.index = None
            self.documents = []
            self.document_metadata = []
        
    def set_comparison_context(self, comparison_data: Dict[str, Any]):
        """Set the current comparison context for the RAG system"""
        self.current_context = {
            "target_company": comparison_data.get("target_company", {}),
            "comparable_companies": comparison_data.get("comparable_companies", []),
            "financial_data": comparison_data.get("financial_data", {}),
            "analysis_timestamp": comparison_data.get("analysis_timestamp"),
            "filters_applied": comparison_data.get("filters", {})
        }
        
        # Index the comparison data for FAISS search
        self._index_comparison_data()
        
    def add_to_conversation(self, user_message: str, assistant_response: str):
        """Add a conversation turn to the history"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "assistant": assistant_response
        })
        
        # Keep only last 10 conversation turns to manage memory
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def _index_comparison_data(self):
        """Index the comparison data for FAISS search"""
        if not self.sentence_model or not self.index:
            return
            
        # Clear existing index
        self.index.reset()
        self.documents = []
        self.document_metadata = []
        
        # Index target company
        target = self.current_context.get("target_company", {})
        if target:
            self._add_document_to_index(
                f"Target company: {target.get('name', 'Unknown')} - {target.get('description', '')}",
                {"type": "target_company", "company": target}
            )
        
        # Index comparable companies
        companies = self.current_context.get("comparable_companies", [])
        for company in companies:
            # Company overview
            company_text = f"Company: {company.get('name', 'Unknown')} ({company.get('ticker', 'N/A')}) - {company.get('rationale', '')}"
            self._add_document_to_index(company_text, {"type": "comparable_company", "company": company})
            
            # Financial metrics
            if company.get("financial_metrics"):
                metrics = company["financial_metrics"]
                financial_text = f"Financial metrics for {company.get('name', 'Unknown')}: "
                financial_text += f"Market cap: {metrics.get('market_cap', 'N/A')}, "
                financial_text += f"P/E ratio: {metrics.get('pe_ratio', 'N/A')}, "
                financial_text += f"ROE: {metrics.get('roe', 'N/A')}, "
                financial_text += f"Net margin: {metrics.get('net_margin', 'N/A')}"
                self._add_document_to_index(financial_text, {"type": "financial_metrics", "company": company})
            
            # Business characteristics
            if company.get("industry") or company.get("business_model"):
                business_text = f"Business profile for {company.get('name', 'Unknown')}: "
                if company.get("industry"):
                    business_text += f"Industry: {company['industry']}, "
                if company.get("business_model"):
                    business_text += f"Business model: {company['business_model']}, "
                if company.get("company_size"):
                    business_text += f"Size: {company['company_size']}, "
                if company.get("geographic_presence"):
                    business_text += f"Geography: {company['geographic_presence']}"
                self._add_document_to_index(business_text, {"type": "business_profile", "company": company})
    
    def _add_document_to_index(self, text: str, metadata: Dict[str, Any]):
        """Add a document to the FAISS index"""
        if not self.sentence_model or not self.index:
            return
            
        try:
            # Generate embedding
            embedding = self.sentence_model.encode([text])
            
            # Add to FAISS index
            self.index.add(embedding)
            
            # Store document and metadata
            self.documents.append(text)
            self.document_metadata.append(metadata)
        except Exception as e:
            print(f"Error indexing document: {e}")
    
    def _search_similar_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar documents using FAISS"""
        if not self.sentence_model or not self.index or self.index.ntotal == 0:
            return []
            
        try:
            # Generate query embedding
            query_embedding = self.sentence_model.encode([query])
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
            
            # Return results with metadata
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.documents):
                    results.append({
                        "text": self.documents[idx],
                        "metadata": self.document_metadata[idx],
                        "score": float(score)
                    })
            
            return results
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def _extract_financial_insights(self, company_data: Dict[str, Any]) -> List[str]:
        """Extract key financial insights from company data"""
        insights = []
        
        if not company_data.get("financial_metrics"):
            return insights
            
        metrics = company_data["financial_metrics"]
        
        # Market cap analysis
        if metrics.get("market_cap") and metrics["market_cap"] != "N/A":
            try:
                market_cap = float(metrics["market_cap"])
                if market_cap > 10000000000:  # > $10B
                    insights.append("Large-cap company (>$10B market cap)")
                elif market_cap > 2000000000:  # > $2B
                    insights.append("Mid-cap company ($2B-$10B market cap)")
                else:
                    insights.append("Small-cap company (<$2B market cap)")
            except:
                pass
        
        # Valuation ratios
        if metrics.get("pe_ratio") and metrics["pe_ratio"] != "N/A":
            try:
                pe = float(metrics["pe_ratio"])
                if pe < 15:
                    insights.append("Low P/E ratio (<15) - potentially undervalued")
                elif pe > 25:
                    insights.append("High P/E ratio (>25) - growth expectations")
            except:
                pass
                
        if metrics.get("pb_ratio") and metrics["pb_ratio"] != "N/A":
            try:
                pb = float(metrics["pb_ratio"])
                if pb < 1:
                    insights.append("Trading below book value (P/B < 1)")
                elif pb > 3:
                    insights.append("High P/B ratio (>3) - premium valuation")
            except:
                pass
        
        # Profitability
        if metrics.get("roe") and metrics["roe"] != "N/A":
            try:
                roe = float(metrics["roe"])
                if roe > 15:
                    insights.append("Strong ROE (>15%) - efficient use of equity")
                elif roe < 5:
                    insights.append("Low ROE (<5%) - efficiency concerns")
            except:
                pass
                
        if metrics.get("net_margin") and metrics["net_margin"] != "N/A":
            try:
                margin = float(metrics["net_margin"])
                if margin > 20:
                    insights.append("High net margin (>20%) - strong profitability")
                elif margin < 5:
                    insights.append("Low net margin (<5%) - thin margins")
            except:
                pass
        
        return insights
    
    def _analyze_comparison_patterns(self) -> Dict[str, Any]:
        """Analyze patterns across comparable companies"""
        if not self.current_context.get("comparable_companies"):
            return {}
            
        companies = self.current_context["comparable_companies"]
        
        # Industry distribution
        industries = {}
        for company in companies:
            if company.get("industry"):
                industries[company["industry"]] = industries.get(company["industry"], 0) + 1
        
        # Size distribution
        sizes = {"large": 0, "medium": 0, "small": 0}
        for company in companies:
            if company.get("company_size"):
                size = company["company_size"].lower()
                if "large" in size or "enterprise" in size:
                    sizes["large"] += 1
                elif "medium" in size or "mid" in size:
                    sizes["medium"] += 1
                else:
                    sizes["small"] += 1
        
        # Geographic distribution
        geographies = {}
        for company in companies:
            if company.get("geographic_presence"):
                geo = company["geographic_presence"]
                geographies[geo] = geographies.get(geo, 0) + 1
        
        return {
            "industry_distribution": industries,
            "size_distribution": sizes,
            "geographic_distribution": geographies,
            "total_companies": len(companies)
        }
    
    def _generate_context_summary(self) -> str:
        """Generate a summary of the current comparison context"""
        if not self.current_context:
            return "No comparison data available."
            
        target = self.current_context.get("target_company", {})
        companies = self.current_context.get("comparable_companies", [])
        
        summary = f"Current analysis: {target.get('name', 'Unknown company')}\n"
        summary += f"Found {len(companies)} comparable companies\n\n"
        
        if target.get("description"):
            summary += f"Target company description: {target['description'][:200]}...\n\n"
        
        # Add key insights from first few companies
        for i, company in enumerate(companies[:3]):
            insights = self._extract_financial_insights(company)
            summary += f"{company.get('name', 'Unknown')} ({company.get('ticker', 'N/A')}): "
            if insights:
                summary += f"{insights[0]}\n"
            else:
                summary += "Financial data available\n"
        
        return summary
    
    def process_query(self, user_query: str) -> str:
        """Process a user query and generate a response using RAG"""
        if not self.current_context:
            return "I don't have any company comparison data to work with. Please run a comparison first."
        
        # Use FAISS search to find relevant documents
        relevant_docs = self._search_similar_documents(user_query, top_k=3)
        
        # Convert query to lowercase for easier matching
        query_lower = user_query.lower()
        
        # Extract context and generate response
        context_summary = self._generate_context_summary()
        patterns = self._analyze_comparison_patterns()
        
        # Generate response using relevant documents and context
        if relevant_docs:
            response = self._generate_enhanced_response(user_query, relevant_docs, context_summary, patterns)
        else:
            # Fallback to rule-based responses
            if any(word in query_lower for word in ["summary", "overview", "what", "tell me"]):
                response = self._handle_summary_query(context_summary, patterns)
            elif any(word in query_lower for word in ["financial", "metrics", "ratios", "valuation"]):
                response = self._handle_financial_query(query_lower)
            elif any(word in query_lower for word in ["industry", "sector", "business"]):
                response = self._handle_industry_query(query_lower, patterns)
            elif any(word in query_lower for word in ["compare", "difference", "similar"]):
                response = self._handle_comparison_query(query_lower)
            elif any(word in query_lower for word in ["recommend", "suggest", "best"]):
                response = self._handle_recommendation_query(query_lower)
            else:
                response = self._handle_general_query(user_query, context_summary)
        
        # Add to conversation history
        self.add_to_conversation(user_query, response)
        
        return response
    
    def _generate_enhanced_response(self, query: str, relevant_docs: List[Dict[str, Any]], 
                                  context_summary: str, patterns: Dict[str, Any]) -> str:
        """Generate enhanced response using FAISS search results"""
        response = f"Based on your query: '{query}'\n\n"
        
        # Add relevant document information
        response += "**Relevant Information Found:**\n"
        for i, doc in enumerate(relevant_docs, 1):
            doc_type = doc["metadata"].get("type", "unknown")
            company_name = doc["metadata"].get("company", {}).get("name", "Unknown")
            
            response += f"{i}. {doc_type.replace('_', ' ').title()} for {company_name}:\n"
            response += f"   {doc['text'][:200]}...\n\n"
        
        # Add context summary
        response += "**Context Summary:**\n"
        response += context_summary + "\n\n"
        
        # Add patterns if available
        if patterns:
            response += "**Key Patterns:**\n"
            if patterns.get("industry_distribution"):
                response += f"- Industry focus: {', '.join(patterns['industry_distribution'].keys())}\n"
            if patterns.get("size_distribution"):
                response += f"- Company sizes: {patterns['size_distribution']['large']} large, {patterns['size_distribution']['medium']} medium, {patterns['size_distribution']['small']} small\n"
        
        # Add follow-up suggestions
        response += "\n**You can ask me about:**\n"
        response += "- Specific companies and their metrics\n"
        response += "- Financial comparisons between companies\n"
        response += "- Industry trends and patterns\n"
        response += "- Investment insights and recommendations\n"
        
        return response
    
    def _handle_summary_query(self, context_summary: str, patterns: Dict[str, Any]) -> str:
        """Handle summary and overview queries"""
        response = context_summary + "\n\n"
        
        if patterns:
            response += "Key patterns:\n"
            if patterns.get("industry_distribution"):
                response += f"- Industry focus: {', '.join(patterns['industry_distribution'].keys())}\n"
            if patterns.get("size_distribution"):
                response += f"- Company sizes: {patterns['size_distribution']['large']} large, {patterns['size_distribution']['medium']} medium, {patterns['size_distribution']['small']} small\n"
            if patterns.get("geographic_distribution"):
                response += f"- Geographic presence: {', '.join(patterns['geographic_distribution'].keys())}\n"
        
        return response
    
    def _handle_financial_query(self, query: str) -> str:
        """Handle financial metrics and ratios queries"""
        companies = self.current_context.get("comparable_companies", [])
        
        if not companies:
            return "No comparable companies available for financial analysis."
        
        response = "Financial analysis of comparable companies:\n\n"
        
        for company in companies[:5]:  # Limit to first 5 for readability
            name = company.get("name", "Unknown")
            ticker = company.get("ticker", "N/A")
            metrics = company.get("financial_metrics", {})
            
            response += f"**{name} ({ticker})**\n"
            
            if metrics:
                insights = self._extract_financial_insights(company)
                if insights:
                    response += f"- {insights[0]}\n"
                else:
                    response += "- Financial data available\n"
            else:
                response += "- No financial data available\n"
            
            response += "\n"
        
        return response
    
    def _handle_industry_query(self, query: str, patterns: Dict[str, Any]) -> str:
        """Handle industry and business model queries"""
        if not patterns.get("industry_distribution"):
            return "No industry data available for analysis."
        
        response = "Industry and business model analysis:\n\n"
        
        # Industry distribution
        response += "**Industry Distribution:**\n"
        for industry, count in patterns["industry_distribution"].items():
            response += f"- {industry}: {count} companies\n"
        
        response += "\n**Business Characteristics:**\n"
        companies = self.current_context.get("comparable_companies", [])
        business_models = {}
        
        for company in companies:
            if company.get("business_model"):
                model = company["business_model"]
                business_models[model] = business_models.get(model, 0) + 1
        
        for model, count in business_models.items():
            response += f"- {model}: {count} companies\n"
        
        return response
    
    def _handle_comparison_query(self, query: str) -> str:
        """Handle comparison and difference queries"""
        companies = self.current_context.get("comparable_companies", [])
        
        if len(companies) < 2:
            return "Need at least 2 companies for comparison analysis."
        
        response = "Company comparison analysis:\n\n"
        
        # Compare first few companies
        for i, company in enumerate(companies[:3]):
            name = company.get("name", "Unknown")
            ticker = company.get("ticker", "N/A")
            rationale = company.get("rationale", "")
            
            response += f"**{name} ({ticker})**\n"
            response += f"Rationale: {rationale[:150]}...\n"
            
            # Add financial comparison if available
            metrics = company.get("financial_metrics", {})
            if metrics:
                insights = self._extract_financial_insights(company)
                if insights:
                    response += f"Key insight: {insights[0]}\n"
            
            response += "\n"
        
        return response
    
    def _handle_recommendation_query(self, query: str) -> str:
        """Handle recommendation and suggestion queries"""
        companies = self.current_context.get("comparable_companies", [])
        
        if not companies:
            return "No companies available for recommendations."
        
        response = "Based on the current comparison data:\n\n"
        
        # Find companies with financial data
        companies_with_financials = [c for c in companies if c.get("financial_metrics")]
        
        if companies_with_financials:
            response += "**Companies with comprehensive financial data:**\n"
            for company in companies_with_financials[:3]:
                name = company.get("name", "Unknown")
                ticker = company.get("ticker", "N/A")
                response += f"- {name} ({ticker})\n"
            
            response += "\n**Recommendations:**\n"
            response += "1. Focus on companies with complete financial metrics for detailed analysis\n"
            response += "2. Consider industry alignment with your target company\n"
            response += "3. Evaluate geographic presence for market expansion insights\n"
        else:
            response += "**Recommendations:**\n"
            response += "1. Run comparison with financial data enabled for deeper insights\n"
            response += "2. Use filters to narrow down to specific industries or company sizes\n"
            response += "3. Consider refining your search criteria for better matches\n"
        
        return response
    
    def _handle_general_query(self, query: str, context_summary: str) -> str:
        """Handle general queries"""
        response = f"I understand you're asking about: {query}\n\n"
        response += "Here's what I can tell you about the current comparison:\n\n"
        response += context_summary
        
        response += "\n\nYou can ask me about:\n"
        response += "- Summary and overview of the comparison\n"
        response += "- Financial metrics and ratios\n"
        response += "- Industry and business model analysis\n"
        response += "- Company comparisons and differences\n"
        response += "- Recommendations and suggestions\n"
        
        return response
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history"""
        return self.conversation_history
    
    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_history = []
    
    def get_context_info(self) -> Dict[str, Any]:
        """Get information about the current context"""
        return {
            "has_context": bool(self.current_context),
            "target_company": self.current_context.get("target_company", {}).get("name", "None"),
            "comparable_count": len(self.current_context.get("comparable_companies", [])),
            "has_financial_data": bool(self.current_context.get("financial_data")),
            "conversation_turns": len(self.conversation_history)
        }
