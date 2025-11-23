"""
Application configuration module.

This module defines application settings using Pydantic Settings for environment
variable management. Includes database, security, CORS, and business logic
configuration options.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings class.

    Centralizes all application configuration with support for environment
    variables, type validation, and computed properties. Settings can be
    overridden via .env file.
    
    Attributes:
        APP_NAME (str): Application name.
        SECRET_KEY (str): Secret key for JWT token signing.
        DATABASE_URL (str): Database connection string.
        CORS_ORIGINS (list): Allowed CORS origins.
        And many other configuration parameters...
    """
    # Application Settings
    APP_NAME: str = "LIMS FastAPI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database Settings
    DATABASE_URL: Optional[str] = None
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 1433
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_DRIVER: str = "SQL Server"
    
    # CORS Settings
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    
    # File Storage Settings
    UPLOAD_DIR: str = "uploads"
    REPORTS_DIR: str = "reports"
    TEMP_DIR: str = "temp"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    # Pagination Settings
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000
    
    # Background Tasks Settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Email Settings (Optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    
    # Report Generation Settings
    REPORT_TEMPLATES_DIR: str = "templates/reports"
    SIGNATURE_DIR: str = "signatures"
    
    # Business Rules Settings
    WORKING_DAYS: list[int] = [0, 1, 2, 3, 4]  # Monday to Friday
    SAMPLE_NUMBER_FORMAT: str = "{type}{date}{sequence:03d}"
    
    @property
    def database_url_sync(self) -> str:
        """Synchronous database URL for SQLAlchemy"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        return (
            f"mssql+pyodbc://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            f"?driver={self.DATABASE_DRIVER.replace(' ', '+')}"
        )
    
    @property
    def database_url_async(self) -> str:
        """Asynchronous database URL for async SQLAlchemy"""
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace("mssql+pyodbc://", "mssql+aioodbc://")
        
        return (
            f"mssql+aioodbc://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            f"?driver={self.DATABASE_DRIVER.replace(' ', '+')}"
        )
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.UPLOAD_DIR,
            self.REPORTS_DIR,
            self.TEMP_DIR,
            self.REPORT_TEMPLATES_DIR,
            self.SIGNATURE_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


# Create global settings instance
settings = Settings()

# Ensure directories exist on startup
settings.ensure_directories()