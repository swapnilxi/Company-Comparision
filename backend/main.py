from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Import routers
from routes import analysis, companies, comparison, market, health, rag

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="AI Analyst for Startup and Enterprise Evaluation API",
    description="API for AI-driven evaluation of startups and enterprises: analyze companies, find comparable peers, fetch financial metrics, and chat via RAG",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(analysis.router)
app.include_router(companies.router)
app.include_router(comparison.router)
app.include_router(market.router)
app.include_router(rag.router)

# Run the application
if __name__ == "__main__":
    # Get host and port from environment variables or use defaults
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run("main:app", host=host, port=port, reload=debug)