"""
LIMS FastAPI - Simple Working Application

This is a simplified version of the LIMS FastAPI application for testing and development.
It provides basic endpoints to verify database connectivity and test API functionality
without the full application structure.

Features:
    - Basic health check and info endpoints
    - Direct database connection testing
    - Sample data retrieval
    - Product and user management
    - Specification management (GEN and CLI types)

Usage:
    This file can be run standalone for quick testing:
    python working_app.py
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic_settings import BaseSettings
import logging

# ========================================
# Configuration
# ========================================
# Simple settings class for database and application configuration
class Settings(BaseSettings):
    APP_NAME: str = "LIMS FastAPI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 1433
    DATABASE_NAME: str = "LIMS_PVS"
    DATABASE_USER: str = "jao"
    DATABASE_PASSWORD: str = "Rie%man123"
    DATABASE_DRIVER: str = "SQL Server"

    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def database_url(self) -> str:
        """
        Generate the database connection URL for SQL Server.

        Returns:
            str: SQLAlchemy connection string for SQL Server
        """
        return (
            f"mssql+pyodbc://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            f"?driver={self.DATABASE_DRIVER.replace(' ', '+')}"
        )

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }

# Initialize settings from environment variables or defaults
settings = Settings()

# ========================================
# Database Setup
# ========================================
# Create database engine and session factory
engine = create_engine(settings.database_url, echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency function to get database session.

    Yields:
        Session: SQLAlchemy database session

    Note:
        Automatically closes the session after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========================================
# FastAPI Application
# ========================================
# Create FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Laboratory Information Management System (LIMS) API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ========================================
# Middleware Configuration
# ========================================
# Configure CORS to allow all origins (for development/testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# API Endpoints
# ========================================
@app.get("/")
async def root():
    """
    Root endpoint with basic API information.

    Returns:
        dict: Welcome message, version, and documentation links
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )

@app.get("/info")
async def app_info():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "database": {
            "host": settings.DATABASE_HOST,
            "port": settings.DATABASE_PORT,
            "name": settings.DATABASE_NAME,
            "driver": settings.DATABASE_DRIVER
        },
        "features": {
            "authentication": "TODO",
            "sample_management": "TODO",
            "report_generation": "TODO",
            "master_data_management": "TODO"
        }
    }

# Basic auth endpoint for testing
@app.post("/auth/test")
async def test_auth():
    return {"message": "Authentication endpoint - TODO: implement JWT"}

# Basic samples endpoint
@app.get("/api/samples")
async def get_samples(db: Session = Depends(get_db)):
    try:
        # Test query to existing tables
        result = db.execute(text("""
            SELECT TOP 5 samplenumber, date, time
            FROM sample
            ORDER BY id DESC
        """))

        samples = []
        for row in result:
            samples.append({
                "sample_number": row[0],
                "date": row[1],
                "time": row[2]
            })

        return {
            "samples": samples,
            "count": len(samples),
            "message": "Successfully retrieved samples from database"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving samples: {str(e)}"
        )

# Master data endpoints
@app.get("/api/products")
async def get_products(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT id, name, bruto FROM product ORDER BY name"))

        products = []
        for row in result:
            products.append({
                "id": row[0],
                "name": row[1],
                "bruto": row[2]
            })

        return {"products": products, "count": len(products)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving products: {str(e)}"
        )

@app.get("/api/users")
async def get_users(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT id, code, name, status, isadmin FROM tuser ORDER BY name"))

        users = []
        for row in result:
            users.append({
                "id": row[0],
                "code": row[1],
                "name": row[2],
                "status": bool(row[3]),
                "is_admin": bool(row[4])
            })

        return {"users": users, "count": len(users)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving users: {str(e)}"
        )

# Helper function to format interval from min/max values
def format_interval(min_val, max_val):
    """Format specification interval as 'min-max' string"""
    if min_val is None and max_val is None:
        return ""

    min_str = str(min_val) if min_val is not None else ""
    max_str = str(max_val) if max_val is not None else ""

    # Handle special case where both are -1 (means any value)
    if min_val == -1 and max_val == -1:
        return "@"

    return f"{min_str}-{max_str}"


@app.get("/api/specifications")
async def get_specifications(
    spec_type: str = "GEN",
    db: Session = Depends(get_db)
):
    """
    Get specifications for products and qualities.

    Args:
        spec_type: Type of specification - 'GEN' for general or 'CLI' for customer-specific

    Returns:
        List of specifications with all variable limits formatted as intervals
    """
    try:
        if spec_type not in ['GEN', 'CLI']:
            raise HTTPException(
                status_code=400,
                detail="spec_type must be either 'GEN' or 'CLI'"
            )

        # First, get all variables with their types
        vars_result = db.execute(text("""
            SELECT id, shortname, typevar
            FROM variable
            ORDER BY ord
        """))

        variables = []
        for row in vars_result:
            variables.append({
                "id": row[0],
                "shortname": row[1],
                "typevar": row[2]  # 'I' for interval, 'L' for list
            })

        # Build the main query based on spec_type
        if spec_type == 'CLI':
            # Customer-specific specifications
            query = text("""
                SELECT
                    s.id,
                    s.Customer,
                    p.name AS Product,
                    q.name AS Quality,
                    s.Status,
                    s.Certificaat,
                    s.Opm,
                    s.COA,
                    s.Day_COA,
                    s.COC,
                    s.Visual,
                    s.OneDecimal,
                    s.min_conc, s.max_conc,
                    s.min_Free_SO3, s.max_Free_SO3,
                    s.min_Free_HCl, s.max_Free_HCl,
                    s.min_pH, s.max_pH,
                    s.min_NH3, s.max_NH3,
                    s.min_ATS, s.max_ATS,
                    s.min_densiteit, s.max_densiteit,
                    s.min_NTU, s.max_NTU,
                    s.min_Particulate_matter, s.max_Particulate_matter,
                    s.min_kleur, s.max_kleur,
                    s.min_SO3, s.max_SO3,
                    s.min_SO2, s.max_SO2,
                    s.min_Cl, s.max_Cl,
                    s.min_Nox, s.max_Nox,
                    s.min_PO4, s.max_PO4,
                    s.min_Kristallisatie, s.max_Kristallisatie,
                    s.min_Residu, s.max_Residu,
                    s.min_Fe, s.max_Fe,
                    s.min_Cr, s.max_Cr,
                    s.min_Ni, s.max_Ni
                FROM spec s
                JOIN product p ON s.product_id = p.id
                JOIN quality q ON s.quality_id = q.id
                WHERE s.typeSpec = 'CLI'
                ORDER BY s.Customer, p.name, q.name
            """)

            result = db.execute(query)
            specifications = []

            for row in result:
                spec = {
                    "id": row[0],
                    "Action": "",
                    "Customer": row[1],
                    "Product": row[2],
                    "Quality": row[3],
                    "Status": row[4],
                    "Certificate": row[5],
                    "Opm": row[6],
                    "COA": row[7],
                    "Day_COA": row[8],
                    "COC": row[9],
                    "Visual": row[10],
                    "OneDecimal": row[11]
                }

                # Add variable intervals (starting from index 12)
                spec["conc"] = format_interval(row[12], row[13])
                spec["Free_SO3"] = format_interval(row[14], row[15])
                spec["Free_HCl"] = format_interval(row[16], row[17])
                spec["pH"] = format_interval(row[18], row[19])
                spec["NH3"] = format_interval(row[20], row[21])
                spec["ATS"] = format_interval(row[22], row[23])
                spec["densiteit"] = format_interval(row[24], row[25])
                spec["NTU"] = format_interval(row[26], row[27])
                spec["Particulate_matter"] = format_interval(row[28], row[29])
                spec["kleur"] = format_interval(row[30], row[31])
                spec["SO3"] = format_interval(row[32], row[33])
                spec["SO2"] = format_interval(row[34], row[35])
                spec["Cl"] = format_interval(row[36], row[37])
                spec["Nox"] = format_interval(row[38], row[39])
                spec["PO4"] = format_interval(row[40], row[41])
                spec["Kristallisatie"] = format_interval(row[42], row[43])
                spec["Residu"] = format_interval(row[44], row[45])
                spec["Fe"] = format_interval(row[46], row[47])
                spec["Cr"] = format_interval(row[48], row[49])
                spec["Ni"] = format_interval(row[50], row[51])

                specifications.append(spec)

        else:  # GEN
            # General specifications
            query = text("""
                SELECT
                    s.id,
                    s.TDS,
                    p.name AS Product,
                    q.name AS Quality,
                    s.Visual,
                    v1.shortname AS Variable1,
                    v2.shortname AS Variable2,
                    v3.shortname AS Variable3,
                    s.min_conc, s.max_conc,
                    s.min_Free_SO3, s.max_Free_SO3,
                    s.min_Free_HCl, s.max_Free_HCl,
                    s.min_pH, s.max_pH,
                    s.min_NH3, s.max_NH3,
                    s.min_ATS, s.max_ATS,
                    s.min_densiteit, s.max_densiteit,
                    s.min_NTU, s.max_NTU,
                    s.min_Particulate_matter, s.max_Particulate_matter,
                    s.min_kleur, s.max_kleur,
                    s.min_SO3, s.max_SO3,
                    s.min_SO2, s.max_SO2,
                    s.min_Cl, s.max_Cl,
                    s.min_Nox, s.max_Nox,
                    s.min_PO4, s.max_PO4
                FROM spec s
                JOIN product p ON s.product_id = p.id
                JOIN quality q ON s.quality_id = q.id
                LEFT JOIN variable v1 ON s.variable1_id = v1.id
                LEFT JOIN variable v2 ON s.variable2_id = v2.id
                LEFT JOIN variable v3 ON s.variable3_id = v3.id
                WHERE s.typeSpec = 'GEN'
                ORDER BY p.name, q.name
            """)

            result = db.execute(query)
            specifications = []

            for row in result:
                spec = {
                    "id": row[0],
                    "Action": "",
                    "TDS": row[1],
                    "Product": row[2],
                    "Quality": row[3],
                    "Visual": row[4],
                    "Variable1": row[5],
                    "Variable2": row[6],
                    "Variable3": row[7]
                }

                # Add variable intervals
                spec["conc"] = format_interval(row[8], row[9])
                spec["Free_SO3"] = format_interval(row[10], row[11])
                spec["Free_HCl"] = format_interval(row[12], row[13])
                spec["pH"] = format_interval(row[14], row[15])
                spec["NH3"] = format_interval(row[16], row[17])
                spec["ATS"] = format_interval(row[18], row[19])
                spec["densiteit"] = format_interval(row[20], row[21])
                spec["NTU"] = format_interval(row[22], row[23])
                spec["Particulate_matter"] = format_interval(row[24], row[25])
                spec["kleur"] = format_interval(row[26], row[27])
                spec["SO3"] = format_interval(row[28], row[29])
                spec["SO2"] = format_interval(row[30], row[31])
                spec["Cl"] = format_interval(row[32], row[33])
                spec["Nox"] = format_interval(row[34], row[35])
                spec["PO4"] = format_interval(row[36], row[37])

                specifications.append(spec)

        return {
            "spec_type": spec_type,
            "specifications": specifications,
            "count": len(specifications)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving specifications: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")