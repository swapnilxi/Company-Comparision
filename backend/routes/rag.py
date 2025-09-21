from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directory to path to import RAG service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag_service import RAGService

router = APIRouter(prefix="/api/rag", tags=["RAG Chatbot"])

# Global RAG service instance
rag_service = RAGService()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_history: List[Dict[str, str]]
    context_info: Dict[str, Any]

class ContextUpdateRequest(BaseModel):
    comparison_data: Dict[str, Any]
    session_id: Optional[str] = None

class ContextUpdateResponse(BaseModel):
    success: bool
    message: str
    context_info: Dict[str, Any]

@router.post("/chat", response_model=ChatResponse)
async def chat_with_rag(request: ChatRequest):
    """Chat with the RAG system about company comparison data"""
    try:
        # Process the user query
        response = rag_service.process_query(request.message)
        
        # Get conversation history and context info
        conversation_history = rag_service.get_conversation_history()
        context_info = rag_service.get_context_info()
        
        return ChatResponse(
            response=response,
            conversation_history=conversation_history,
            context_info=context_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG processing error: {str(e)}")

@router.post("/update-context", response_model=ContextUpdateResponse)
async def update_rag_context(request: ContextUpdateRequest):
    """Update the RAG system context with new comparison data"""
    try:
        # Update the RAG service context
        rag_service.set_comparison_context(request.comparison_data)
        
        # Get updated context info
        context_info = rag_service.get_context_info()
        
        return ContextUpdateResponse(
            success=True,
            message="RAG context updated successfully",
            context_info=context_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context update error: {str(e)}")

@router.get("/context-info")
async def get_context_info():
    """Get information about the current RAG context"""
    try:
        context_info = rag_service.get_context_info()
        return context_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting context info: {str(e)}")

@router.post("/clear-conversation")
async def clear_conversation():
    """Clear the conversation history"""
    try:
        rag_service.clear_conversation()
        return {"success": True, "message": "Conversation history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing conversation: {str(e)}")

@router.get("/conversation-history")
async def get_conversation_history():
    """Get the current conversation history"""
    try:
        history = rag_service.get_conversation_history()
        return {"conversation_history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversation history: {str(e)}")
