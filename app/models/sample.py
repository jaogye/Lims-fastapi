"""
Sample database models module.

This module defines the database models related to samples and their measurements
in the LIMS system, including Sample, Measurement, and Map models for managing
laboratory sample data and test results.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Numeric, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class Sample(BaseModel):
    """
    Sample model representing laboratory samples.

    Stores information about samples collected for testing, including production
    samples (PRO), customer samples (CLI), and manual samples (MAN). Each sample
    is linked to a product, quality, and optional specification.

    Attributes:
        type_sample (str): Sample type - PRO (production), CLI (customer), or MAN (manual).
        spec_id (int): Foreign key to specification table.
        product_id (int): Foreign key to product table.
        quality_id (int): Foreign key to quality table.
        sample_matrix_id (int): Foreign key to sample matrix table.
        created_by_id (int): Foreign key to user who created the sample.
        creation_date (str): Date and time when sample was created.
        date (str): Sample collection date.
        time (str): Sample collection time.
        order_number_pvs (int): Internal PVS order number.
        article_no (int): Article number.
        order_number_client (str): Customer order number.
        description (str): Sample description.
        loading_ton (Decimal): Loading amount in tons.
        sample_number (str): Unique sample identifier.
        remark (str): Additional remarks.
        batch_number (str): Batch number.
        container_number (str): Container number.
        customer (str): Customer name.
        sample_point_id (int): Foreign key to sample point table.
        samplepoint_name (str): Sample point name (tank name).
        certificate (str): Certificate indicator.
        coc (str): Certificate of Conformity indicator (X/N).
        day_coa (str): Daily Certificate of Analysis indicator (X/N).
        coa (str): Certificate of Analysis indicator (X/N).
    """
    __tablename__ = "sample"
    
    type_sample = Column(String(3), nullable=False)  # PRO, CLI, MAN
    spec_id = Column(Integer, ForeignKey("spec.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quality_id = Column(Integer, ForeignKey("quality.id"), nullable=False)
    sample_matrix_id = Column(Integer, ForeignKey("samplematrix.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("tuser.id"), nullable=True)
    creation_date = Column(String(20), nullable=True)
    date = Column(String(10), nullable=True)
    time = Column(String(20), nullable=True)
    order_number_pvs = Column(Integer, nullable=True)
    article_no = Column(Integer, nullable=True)
    order_number_client = Column(String(40), nullable=True)
    description = Column(String(60), nullable=True)
    loading_ton = Column(Numeric(12, 6), nullable=True)
    sample_number = Column(String(23), nullable=True)
    remark = Column(String(100), nullable=True)
    batch_number = Column(String(20), nullable=True)
    container_number = Column(String(20), nullable=True)
    customer = Column(String(60), nullable=True)
    sample_point_id = Column(Integer, ForeignKey("samplepoint.id"), nullable=True)
    samplepoint_name = Column(String(50), nullable=True)
    certificate = Column(String(1), nullable=True)
    coc = Column(String(1), nullable=True)
    day_coa = Column(String(1), nullable=True)
    coa = Column(String(1), nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="samples")
    quality = relationship("Quality", back_populates="samples")
    sample_point = relationship("SamplePoint", back_populates="samples")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_samples")
    spec = relationship("Spec", back_populates="samples")
    sample_matrix = relationship("SampleMatrix", back_populates="samples")
    measurements = relationship("Measurement", back_populates="sample")


class Measurement(BaseModel):
    """
    Measurement model for test results.

    Stores individual test measurements for samples, including the tested variable,
    value, limits, and testing metadata. Each measurement is linked to a specific
    sample and variable.

    Attributes:
        sample_id (int): Foreign key to sample table.
        variable (str): Variable name being measured.
        tested_by_id (int): Foreign key to user who performed the test.
        test_date (str): Date and time when test was performed.
        min_value (Decimal): Minimum acceptable value for this variable.
        value (Decimal): Actual measured value.
        max_value (Decimal): Maximum acceptable value for this variable.
        variable_id (int): Foreign key to variable table.
        less (bool): Indicates if value is less than detection limit.
    """
    __tablename__ = "measurement"
    
    sample_id = Column(Integer, ForeignKey("sample.id"), nullable=False)
    variable = Column(String(20), nullable=False)
    tested_by_id = Column(Integer, ForeignKey("tuser.id"), nullable=True)
    test_date = Column(String(20), nullable=True)
    min_value = Column(Numeric(12, 6), nullable=True)
    value = Column(Numeric(12, 6), nullable=True)
    max_value = Column(Numeric(12, 6), nullable=True)
    variable_id = Column(Integer, ForeignKey("variable.id"), nullable=True)
    less = Column(Boolean, nullable=True)
    
    # Relationships
    sample = relationship("Sample", back_populates="measurements")
    tested_by = relationship("User", foreign_keys=[tested_by_id], back_populates="tested_measurements")
    variable = relationship("Variable", back_populates="measurements")


class Map(BaseModel):
    """
    Map model for article code mapping.

    Maps article codes to product and quality combinations, providing a link
    between external article numbers and internal product/quality classifications.
    Used for customer order processing and logistic data integration.

    Attributes:
        article_code (int): External article code number.
        product_id (int): Foreign key to product table.
        quality_id (int): Foreign key to quality table.
        logistic_info (str): Additional logistic information.
    """
    __tablename__ = "map"
    
    article_code = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quality_id = Column(Integer, ForeignKey("quality.id"), nullable=False)
    logistic_info = Column(String(40), nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="maps")
    quality = relationship("Quality", back_populates="maps")