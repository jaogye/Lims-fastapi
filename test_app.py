"""
LIMS FastAPI - Basic Test Application

A minimal FastAPI application for testing that the framework is installed
and working correctly. This does not connect to the database.

Usage:
    python test_app.py

Then visit http://localhost:8000/docs to see the API documentation.
"""

from fastapi import FastAPI

# Create minimal FastAPI application
app = FastAPI(
    title="LIMS FastAPI Test",
    version="1.0.0",
    description="Test version to verify FastAPI is working"
)

@app.get("/")
async def root():
    """
    Root endpoint - returns a simple message.

    Returns:
        dict: Welcome message and status
    """
    return {"message": "Hello from LIMS FastAPI!", "status": "working"}

@app.get("/health")
async def health():
    """
    Health check endpoint - confirms API is running.

    Returns:
        dict: Health status (database not tested in this version)
    """
    return {"status": "healthy", "database": "not connected (test mode)"}

# Application entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)