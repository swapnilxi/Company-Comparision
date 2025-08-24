from fastapi import APIRouter

# Initialize router
router = APIRouter(tags=["health"])

@router.get("/")
async def read_root():
    """Root endpoint"""
    return {"message": "Welcome to the Company Comparison API"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}



