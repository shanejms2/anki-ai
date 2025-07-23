from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import get_logger
# from app.core.middleware import setup_middleware
# from app.core.docs import setup_documentation
from app.api.v1.auth import router as auth_router
from app.api.v1.cards import router as cards_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.system import router as system_router
import structlog
from app.core.middleware import SecurityMiddleware, RateLimitMiddleware, LoggingMiddleware

# Initialize logger
logger = get_logger()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    description="Anki-AI Backend API for spaced repetition flashcard system"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Comment out all custom middleware for debugging
# from app.core.middleware import (
#     InputValidationMiddleware,
#     LoggingMiddleware,
#     SecurityMiddleware,
#     RateLimitMiddleware,
# )

# app.add_middleware(InputValidationMiddleware)
# app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# Setup API documentation
# setup_documentation(app)

# Include API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(cards_router, prefix="/api/v1")
app.include_router(reviews_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Starting Anki-AI Backend", version=settings.app_version)
    logger.info("Environment", env=settings.environment)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down Anki-AI Backend")


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Welcome to Anki-AI Backend",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test Supabase connection by querying an existing table
        from app.core.supabase import get_supabase
        supabase = get_supabase()
        
        # Test connection by querying the users table (which should exist)
        # We'll just count the total rows to verify connection
        response = supabase.table("users").select("id", count="exact").limit(1).execute()
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": settings.app_version,
            "database_tables": "accessible"
        }
    except Exception as e:
        logger.warning("Health check database test failed", error=str(e))
        # Don't fail the health check completely, just note the database issue
        return {
            "status": "degraded",
            "database": "connection_issue",
            "version": settings.app_version,
            "warning": "Database connection test failed, but API is running"
        }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 
    

# uvicorn app.main:app --reload