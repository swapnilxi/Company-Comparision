# RAG Chatbot Implementation

## Overview

This document describes the implementation of a Retrieval-Augmented Generation (RAG) chatbot system for the Company Comparison application. The chatbot provides intelligent analysis and insights about company comparison results using both rule-based logic and vector similarity search.

## Architecture

### Backend Components

#### 1. RAG Service (`backend/rag_service.py`)
- **Core RAG Engine**: Processes user queries and generates contextual responses
- **FAISS Integration**: Uses FAISS for vector similarity search of company data
- **Document Indexing**: Automatically indexes comparison data for semantic search
- **Context Management**: Maintains conversation history and current analysis context

#### 2. RAG API Routes (`backend/routes/rag.py`)
- **Chat Endpoint**: `/api/rag/chat` - Process user messages
- **Context Update**: `/api/rag/update-context` - Update RAG context with new data
- **Context Info**: `/api/rag/context-info` - Get current context information
- **Conversation Management**: Clear history and retrieve conversation logs

#### 3. Main Application Integration (`backend/main.py`)
- Includes RAG router for API endpoints
- Integrates with existing company comparison functionality

### Frontend Components

#### 1. RAG Chatbot Component (`frontend/src/components/RAGChatbot.tsx`)
- **Floating Chat Interface**: Right sidebar chatbot with toggle functionality
- **Real-time Chat**: Interactive conversation with the AI assistant
- **Context Awareness**: Automatically updates when comparison data changes
- **Suggested Questions**: Provides helpful question suggestions for users

#### 2. Main Page Integration (`frontend/src/app/page.tsx`)
- Integrates chatbot with existing comparison workflow
- Passes comparison data to chatbot for context

## Features

### Core RAG Capabilities
- **Semantic Search**: Uses FAISS and sentence transformers for intelligent document retrieval
- **Context-Aware Responses**: Generates responses based on current comparison data
- **Financial Analysis**: Provides insights on financial metrics, ratios, and valuations
- **Industry Patterns**: Identifies trends across comparable companies
- **Investment Insights**: Offers recommendations and analysis suggestions

### User Experience Features
- **Iterative Conversations**: Users can ask follow-up questions
- **Suggested Questions**: Pre-built question templates for common queries
- **Real-time Updates**: Context automatically updates with new comparison data
- **Conversation History**: Maintains chat history for context continuity
- **Responsive Design**: Mobile-friendly chat interface

### Technical Features
- **FAISS Vector Search**: High-performance similarity search
- **Sentence Embeddings**: Uses 'all-MiniLM-L6-v2' model for text encoding
- **Document Chunking**: Intelligent indexing of company data
- **Fallback Logic**: Rule-based responses when vector search unavailable
- **Error Handling**: Graceful degradation and user-friendly error messages

## Installation & Setup

### Backend Dependencies
```bash
# Install RAG-specific dependencies
pip install sentence-transformers faiss-cpu numpy

# Or install all requirements
pip install -r requirements.txt
```

### Frontend Dependencies
```bash
# No additional dependencies required
# Uses existing React/Next.js setup
```

## Usage

### Starting the Backend
```bash
cd backend
python main.py
```

### Starting the Frontend
```bash
cd frontend
npm run dev
```

### Testing the RAG Service
```bash
cd backend
python test_rag.py
```

## API Endpoints

### POST `/api/rag/chat`
Send a message to the RAG chatbot.

**Request:**
```json
{
  "message": "Give me a summary of the comparison",
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "response": "AI-generated response...",
  "conversation_history": [...],
  "context_info": {...}
}
```

### POST `/api/rag/update-context`
Update the RAG context with new comparison data.

**Request:**
```json
{
  "comparison_data": {
    "target_company": {...},
    "comparable_companies": [...],
    "financial_data": {...}
  }
}
```

### GET `/api/rag/context-info`
Get information about the current RAG context.

### POST `/api/rag/clear-conversation`
Clear the conversation history.

### GET `/api/rag/conversation-history`
Retrieve the current conversation history.

## Data Flow

1. **User runs comparison** → Comparison data generated
2. **RAG context updated** → Data indexed in FAISS
3. **User asks question** → Query processed through RAG
4. **Vector search** → Relevant documents retrieved
5. **Response generation** → Contextual answer created
6. **Conversation updated** → History maintained for follow-ups

## Query Types Handled

### Summary & Overview
- "Give me a summary of the comparison"
- "What companies were found?"
- "Tell me about the analysis"

### Financial Analysis
- "Which companies have the best financial metrics?"
- "What are the P/E ratios?"
- "Show me profitability analysis"

### Industry & Business
- "What are the key industry patterns?"
- "Compare business models"
- "Show geographic distribution"

### Comparisons
- "Compare the top 3 companies"
- "What are the differences?"
- "Which is most similar?"

### Recommendations
- "What investment insights can you provide?"
- "Which companies should I focus on?"
- "Give me recommendations"

## Customization

### Adding New Query Types
1. Add pattern matching in `process_query()` method
2. Implement handler method (e.g., `_handle_custom_query()`)
3. Update response generation logic

### Modifying Response Format
1. Edit response templates in handler methods
2. Adjust FAISS search parameters
3. Modify document indexing strategy

### Extending Context
1. Add new fields to comparison data
2. Update indexing logic in `_index_comparison_data()`
3. Enhance context summary generation

## Performance Considerations

### FAISS Index Management
- Index is rebuilt when context changes
- Documents are chunked for optimal search
- Vector dimensions: 384 (all-MiniLM-L6-v2)

### Memory Management
- Conversation history limited to 10 turns
- Document metadata stored efficiently
- Graceful fallback when ML dependencies unavailable

### Scalability
- Stateless API design
- Efficient vector search with FAISS
- Minimal memory footprint per request

## Troubleshooting

### Common Issues

1. **FAISS/SentenceTransformer not available**
   - Install dependencies: `pip install sentence-transformers faiss-cpu`
   - Service falls back to rule-based responses

2. **Chatbot not responding**
   - Check backend API is running
   - Verify comparison data is available
   - Check browser console for errors

3. **Context not updating**
   - Ensure comparison data is passed correctly
   - Check API endpoint responses
   - Verify data format matches expected schema

### Debug Mode
- Enable debug logging in backend
- Check API response status codes
- Monitor conversation history updates

## Future Enhancements

### Planned Features
- **Multi-language Support**: Internationalization for global users
- **Advanced Analytics**: Deeper financial analysis and insights
- **Export Functionality**: Save conversations and analysis reports
- **Integration APIs**: Connect with external data sources

### Technical Improvements
- **Caching**: Redis integration for response caching
- **Model Optimization**: Fine-tuned models for financial domain
- **Real-time Updates**: WebSocket integration for live updates
- **Advanced Search**: Hybrid search combining vector and keyword approaches

## Contributing

### Development Guidelines
1. Follow existing code structure and patterns
2. Add comprehensive error handling
3. Include unit tests for new functionality
4. Update documentation for API changes
5. Maintain backward compatibility

### Testing
- Run `python test_rag.py` for backend testing
- Test frontend integration with various data scenarios
- Verify error handling and edge cases
- Performance testing with large datasets

## License

This implementation is part of the Company Comparison application and follows the same licensing terms.

