"""
Laboratory master data database models module.

This module defines master data models used throughout the laboratory system,
including Variables, Products, Qualities, Sample Points, and Holidays. These
models represent the foundational reference data for the LIMS system.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Numeric, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class Variable(BaseModel):
    """
    Test variable model.

    Defines testable variables/parameters in the laboratory, such as pH,
    concentration, trace elements, etc. Each variable has a name, test method,
    unit, and type classification.

    Attributes:
        name (str): Variable name (e.g., 'pH', 'Fe', 'Conc').
        test (str): Test method or procedure name.
        element (str): Chemical element symbol if applicable.
        unit (str): Measurement unit (e.g., 'mg/L', '%', 'ppm').
        ord (int): Display order for sorting variables.
        typevar (str): Variable type - 'I' (interval) or 'L' (list/categorical).
    """
    __tablename__ = "variable"
    
    name = Column(String(20), nullable=False)
    test = Column(String(40), nullable=False)
    element = Column(String(40), nullable=True)
    unit = Column(String(20), nullable=True)
    ord = Column(Integer, nullable=True)
    typevar = Column(String(1), nullable=True)
    
    # Relationships
    sample_matrix_variables = relationship("SampleMatrixVariable", back_populates="variable")
    spec_variables = relationship("SpecVariable", back_populates="variable")
    measurements = relationship("Measurement", back_populates="variable")


class Product(BaseModel):
    """
    Product model for chemical products.

    Represents chemical products manufactured or distributed by the company.
    Products are linked to qualities, specifications, and samples.

    Attributes:
        name (str): Product name.
        bruto (str): Gross product information.
        name_coa (str): Product name as it appears on Certificates of Analysis.
    """
    __tablename__ = "product"

    name = Column(String(60), nullable=False)
    bruto = Column(String(40), nullable=True)
    name_coa = Column(String(40), nullable=True)

    # Relationships
    samples = relationship("Sample", back_populates="product")
    sample_matrices = relationship("SampleMatrix", back_populates="product")
    specs = relationship("Spec", back_populates="product")
    maps = relationship("Map", back_populates="product")


class Quality(BaseModel):
    """
    Quality grade model.

    Defines quality grades or classifications for products. Each product can
    have multiple quality grades with different specifications.

    Attributes:
        name (str): Short quality name/code.
        long_name (str): Full descriptive quality name.
    """
    __tablename__ = "quality"

    name = Column(String(60), nullable=False)
    long_name = Column(String(60), nullable=True)

    # Relationships
    samples = relationship("Sample", back_populates="quality")
    sample_matrices = relationship("SampleMatrix", back_populates="quality")
    specs = relationship("Spec", back_populates="quality")
    maps = relationship("Map", back_populates="quality")


class SamplePoint(BaseModel):
    """
    Sample point model.

    Defines physical locations where samples are collected in the production
    or distribution process (e.g., 'Tank 1', 'Loading Station A').

    Attributes:
        name (str): Sample point name/location identifier.
    """
    __tablename__ = "samplepoint"

    name = Column(String(40), nullable=False)

    # Relationships
    samples = relationship("Sample", back_populates="sample_point")
    sample_matrices = relationship("SampleMatrix", back_populates="sample_point")


class Holidays(BaseModel):
    """
    Holidays model.

    Stores company holidays and non-working days. Used for scheduling
    sample collections and determining first working days of periods.

    Attributes:
        date (str): Holiday date in string format (YYYY-MM-DD).
    """
    __tablename__ = "holidays"

    date = Column(String(10), nullable=False, unique=True)