from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from datetime import datetime
import logging

# Import configuration
from config import get_settings, setup_logging

# Import route handlers
from routes import health_router, subscription_router

# Initialize settings
settings = get_settings()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="AEGIS FIT Backend API",
    description="Backend API for AEGIS FIT fitness tracking application with subscription management",
    version="1.0.0",
    docs_url="/docs" if settings.should_show_docs() else None,
    redoc_url="/redoc" if settings.should_show_docs() else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - returns service information"""
    return {
        "message": "AEGIS FIT Backend API",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "docs_url": "/docs" if settings.should_show_docs() else None,
        "environment": settings.environment
    }

# Include route handlers
app.include_router(health_router, prefix="/api")
app.include_router(subscription_router)

# API info endpoint
@app.get("/api/info")
async def api_info():
    """Get API information and configuration"""
    return {
        "api_name": "AEGIS FIT Backend",
        "version": "1.0.0",
        "description": "Backend API for AEGIS FIT fitness tracking application",
        "environment": settings.environment,
        "features": {
            "stripe_enabled": settings.is_stripe_configured(),
            "email_enabled": settings.is_email_configured(),
            "cors_enabled": True,
            "docs_enabled": settings.should_show_docs(),
            "debug_mode": settings.debug
        },
        "endpoints": {
            "root": "/",
            "health": "/api/health",
            "docs": "/docs",
            "subscription_plans": "/subscription/plans",
            "create_subscription": "/subscription/create",
            "subscription_status": "/subscription/status/{user_id}",
            "webhook": "/subscription/webhook"
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url.path)
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 AEGIS FIT Backend starting up...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Stripe configured: {settings.is_stripe_configured()}")
    logger.info(f"Email configured: {settings.is_email_configured()}")
    logger.info(f"CORS origins: {settings.get_cors_origins()}")
    logger.info(f"API docs enabled: {settings.should_show_docs()}")
    
    if settings.debug:
        logger.warning("⚠️ Debug mode is enabled - this should not be used in production")
    
    logger.info("✅ AEGIS FIT Backend started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("🛑 AEGIS FIT Backend shutting down...")
    logger.info("✅ AEGIS FIT Backend shutdown complete")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting AEGIS FIT Backend with uvicorn...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.auto_reload and settings.is_development(),
        log_level=settings.get_log_level().lower(),
        access_log=True
    )