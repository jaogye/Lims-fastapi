"""
Database connection module.

This module handles database connectivity, session management, and provides
utility functions for database operations including connection testing,
table creation, and raw SQL execution.
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.database_url_sync,
    poolclass=NullPool,  # Use NullPool for SQL Server with pyodbc
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,   # Verify connections before use
    pool_recycle=3600,    # Recycle connections every hour
    use_setinputsizes=False,  # Fix for SQL Server ODBC precision issues
    connect_args={
        "check_same_thread": False,  # For SQLite compatibility if needed
        "timeout": 30,  # Connection timeout
    }
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set database-specific connection parameters"""
    # This event listener can be used to set specific connection parameters
    # For SQL Server, we might want to set specific options
    pass


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {type(e).__name__}: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    try:
        from ..models.base import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def test_connection() -> bool:
    """Test database connection"""
    try:
        db = SessionLocal()
        # Try to execute a simple query
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


class DatabaseManager:
    """
    Database management utilities class.

    Provides static methods for database operations including session management,
    raw SQL execution, and database backup functionality.
    """

    @staticmethod
    def get_session() -> Session:
        """
        Get a new database session.

        Returns:
            Session: New SQLAlchemy database session.
        """
        return SessionLocal()
    
    @staticmethod
    def close_session(session: Session):
        """Close database session safely"""
        try:
            session.close()
        except Exception as e:
            logger.error(f"Error closing session: {e}")
    
    @staticmethod
    def execute_raw_sql(sql: str, params: dict = None) -> list:
        """Execute raw SQL query"""
        session = SessionLocal()
        try:
            result = session.execute(text(sql), params or {})
            return result.fetchall()
        except Exception as e:
            logger.error(f"Error executing raw SQL: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    @staticmethod
    def backup_database(backup_path: str) -> bool:
        """Backup database (SQL Server specific)"""
        try:
            sql = f"""
            BACKUP DATABASE [{settings.DATABASE_NAME}] 
            TO DISK = '{backup_path}'
            WITH FORMAT, INIT, COMPRESSION
            """
            DatabaseManager.execute_raw_sql(sql)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False