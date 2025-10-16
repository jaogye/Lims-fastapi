"""
Base database models module.

This module provides the foundational SQLAlchemy model classes used throughout
the LIMS application. It defines the declarative base and a base model with
common fields for all database entities.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, Boolean, func
from typing import Any
from datetime import datetime

Base = declarative_base()


class BaseModel(Base):
    """
    Abstract base model for all database entities.

    Provides common fields and functionality shared across all models including
    automatic ID generation and timestamp tracking for creation and updates.
    All models in the application should inherit from this base class.

    Attributes:
        id (int): Primary key, auto-incrementing integer identifier.
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp when the record was last updated.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert model instance to dictionary.

        Converts all column values of the model to a dictionary representation,
        useful for serialization and API responses.

        Returns:
            dict[str, Any]: Dictionary containing all column names as keys and
                their corresponding values.
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}