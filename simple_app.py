"""
LIMS FastAPI - Simple Database Test Application

A test application for verifying database connectivity with the LIMS SQL Server database.
Provides endpoints to test connection, query tables, and validate database setup.

Features:
    - Database connection testing
    - Table listing
    - Basic health checks

Usage:
    python simple_app.py

Endpoints:
    - GET / - Basic info with sanitized database URL
    - GET /test-db - Test database connection
    - GET /test-tables - List available database tables
"""

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from pydantic_settings import BaseSettings
import logging

# ========================================
# Configuration
# ========================================
# Simple settings for database connection
class Settings(BaseSettings):
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 1433
    DATABASE_NAME: str = "LIMS_PVS"
    DATABASE_USER: str = "jao"
    DATABASE_PASSWORD: str = "Rie%man123"
    DATABASE_DRIVER: str = "ODBC Driver 17 for SQL Server"

    @property
    def database_url(self) -> str:
        """
        Generate SQL Server connection URL.

        Returns:
            str: SQLAlchemy database connection string
        """
        return (
            f"mssql+pyodbc://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            f"?driver={self.DATABASE_DRIVER.replace(' ', '+')}"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env

# Initialize settings
settings = Settings()

# ========================================
# Logging Setup
# ========================================
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(title="LIMS Simple Test", version="1.0.0")

# ========================================
# API Endpoints
# ========================================
@app.get("/")
async def root():
    """
    Root endpoint with database configuration info.

    Returns:
        dict: Message and sanitized database URL
    """
    return {
        "message": "LIMS FastAPI with Database Test",
        "database_url": settings.database_url.replace(settings.DATABASE_PASSWORD, "***")
    }

@app.get("/test-db")
async def test_database():
    """
    Test database connection with a simple query.

    Returns:
        dict: Success status and query result

    Raises:
        HTTPException: 500 if database connection fails
    """
    try:
        logger.info(f"Testing database connection to: {settings.database_url.replace(settings.DATABASE_PASSWORD, '***')}")

        # Create engine and test connection
        engine = create_engine(settings.database_url, echo=True)

        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            row = result.fetchone()

        return {
            "status": "success",
            "message": "Database connection successful",
            "test_query_result": row[0] if row else None
        }

    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )

@app.get("/test-tables")
async def test_tables():
    """
    List database tables in the LIMS database.

    Returns:
        dict: Success status, database name, count and list of tables

    Raises:
        HTTPException: 500 if query fails
    """
    try:
        engine = create_engine(settings.database_url)

        with engine.connect() as connection:
            # Check if LIMS_PVS database exists and list some tables
            result = connection.execute(text("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """))

            tables = [row[0] for row in result.fetchall()]

        return {
            "status": "success",
            "database": settings.DATABASE_NAME,
            "tables_found": len(tables),
            "tables": tables[:10]  # Show first 10 tables
        }

    except Exception as e:
        logger.error(f"Failed to query tables: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query tables: {str(e)}"
        )

# ========================================
# Application Entry Point
# ========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")