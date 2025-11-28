"""
LIMS FastAPI Application - Main Entry Point

This is the main FastAPI application for the Laboratory Information Management System (LIMS).
It provides RESTful API endpoints for managing samples, generating reports, handling authentication,
and managing master data.

Key Features:
    - Sample management and tracking
    - Report generation (COA, COC, certificates)
    - User authentication with JWT tokens
    - Master data management (products, qualities, variables)
    - Background task processing
    - Comprehensive error handling and logging

The application uses:
    - FastAPI for the web framework
    - SQLAlchemy for database ORM
    - SQL Server as the database backend
    - JWT tokens for authentication
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import sys
import os

from app.core.config  import settings
from app.database.connection import get_db, test_connection, create_tables
from app.api import auth, samples, reports, master_data, users

# ========================================
# Logging Configuration
# ========================================
# Configure logging to output to both file and console
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


# ========================================
# Application Lifespan Management
# ========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application lifespan (startup and shutdown events).
    
    Startup tasks:
        - Test database connection
        - Initialize database tables
        - Log application startup
    
    Shutdown tasks:
        - Log application shutdown
        - Clean up resources
    """
    # Startup phase
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Test database connection
    if not test_connection():
        logger.error("Database connection failed")
        raise Exception("Cannot connect to database")
    
    # Create tables if they don't exist (skip if error occurs)
    try:
        create_tables()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.warning(f"Could not create tables automatically: {e}")
        logger.info("Tables may already exist or need manual creation")
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown phase
    logger.info("Shutting down application")


# ========================================
# FastAPI Application Instance
# ========================================
# Create the main FastAPI application with documentation endpoints
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Laboratory Information Management System (LIMS) API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ========================================
# Middleware Configuration
# ========================================
# Configure Cross-Origin Resource Sharing (CORS) to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# ========================================
# Exception Handlers
# ========================================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    Handle request validation errors.
    
    Returns a structured JSON response with validation error details.
    """
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation Error",
            "errors": exc.errors()
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Handle standard HTTP exceptions.
    
    Returns a structured JSON response with HTTP error details.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Handle all unhandled exceptions.

    Logs the error and returns a generic error response to avoid exposing internals.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


# ========================================
# Router Registration
# ========================================
# Include API routers for different modules
app.include_router(auth.router)  # Authentication endpoints
app.include_router(samples.router)  # Sample management endpoints
app.include_router(reports.router)  # Report generation endpoints
app.include_router(master_data.router)  # Master data endpoints
app.include_router(users.router)  # User administration endpoints


# ========================================
# API Endpoints
# ========================================
@app.get("/api")
async def root():
    """
    Root endpoint - provides basic information about the API.

    Returns:
        dict: Welcome message with API version and documentation links
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint - verifies the API and database are operational.

    Returns:
        dict: Health status, version, and database connection status

    Raises:
        HTTPException: 503 if database connection fails
    """
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable - database connection failed"
        )


@app.get("/info")
async def app_info():
    """
    Application information endpoint - provides detailed application metadata.

    Returns:
        dict: Application name, version, configuration, and feature list
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "database": {
            "host": settings.DATABASE_HOST,
            "port": settings.DATABASE_PORT,
            "name": settings.DATABASE_NAME
        },
        "features": {
            "authentication": True,
            "sample_management": True,
            "report_generation": True,
            "master_data_management": True,
            "background_tasks": True
        }
    }


# ========================================
# Static Files (Frontend)
# ========================================
# Mount static files last - this should come after all API routes
# Serves the built React frontend from the static directory
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")


# ========================================
# Application Entry Point
# ========================================
if __name__ == "__main__":
    import uvicorn

    # Run the application using Uvicorn ASGI server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,  # Default port
        reload=settings.DEBUG,  # Enable auto-reload in debug mode
        log_level=settings.LOG_LEVEL.lower()  # Set logging level from settings
    )