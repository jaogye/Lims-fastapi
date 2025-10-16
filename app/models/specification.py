"""
Specification database models module.

This module defines database models for product specifications, sample matrices,
and testing requirements. It includes models for general and customer-specific
specifications, along with sample matrix configurations that define which tests
should be performed for different product/quality/sample point combinations.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Numeric, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class Spec(BaseModel):
    """
    Specification model for product quality specifications.

    Defines quality specifications for products including chemical limits,
    trace element limits, and certification requirements. Supports both
    general specifications (GEN) and customer-specific specifications (CLI).

    Attributes:
        type_spec (str): Specification type - GEN (general) or CLI (customer-specific).
        product_id (int): Foreign key to product table.
        quality_id (int): Foreign key to quality table.
        variable1_id (int): Foreign key to first custom variable.
        variable2_id (int): Foreign key to second custom variable.
        variable3_id (int): Foreign key to third custom variable.
        status (str): Specification status - ACTIVE or INACTIVE.
        certificate (str): Certificate requirement indicator.
        opm (str): Notes or remarks (up to 200 characters).
        day_coa (str): Daily Certificate of Analysis requirement.
        visual (str): Visual inspection notes.
        coc (str): Certificate of Conformity requirement.
        coa (Decimal): Certificate of Analysis configuration.
        customer (Decimal): Customer reference number.
        tds (str): Technical Data Sheet reference.
        min_* (Decimal): Minimum values for various chemical parameters and trace elements.
        max_* (Decimal): Maximum values for various chemical parameters and trace elements.

    Note:
        This model contains extensive min/max fields for numerous chemical parameters
        and trace elements (conc, free_so3, ph, fe, cr, ni, as, etc.) to support
        comprehensive chemical analysis specifications.
    """
    __tablename__ = "spec"
    type_spec = Column(String(3), nullable=False)  # GEN, CLI
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quality_id = Column(Integer, ForeignKey("quality.id"), nullable=False)
    variable1_id = Column(Integer, ForeignKey("variable.id"), nullable=True)
    variable2_id = Column(Integer, ForeignKey("variable.id"), nullable=True)
    variable3_id = Column(Integer, ForeignKey("variable.id"), nullable=True)
    status = Column(String(10), nullable=True)  # ACTIVE, INACTIVE
    certificate = Column(String(1), nullable=True)
    opm = Column(String(200), nullable=True)
    day_coa = Column(String(1), nullable=True)
    visual = Column(String(60), nullable=True)
    coc = Column(String(1), nullable=True)
    coa = Column(Numeric(12, 6), nullable=True)
    customer = Column(Numeric(12, 6), nullable=True)
    tds = Column(String(20), nullable=True)
    
    # Chemical limits - minimum values
    min_conc = Column(Numeric(12, 6), nullable=True)
    min_free_so3 = Column(Numeric(12, 6), nullable=True)
    min_free_hcl = Column(Numeric(12, 6), nullable=True)
    min_ph = Column(Numeric(12, 6), nullable=True)
    min_nh3 = Column(Numeric(12, 6), nullable=True)
    min_ats = Column(Numeric(12, 6), nullable=True)
    min_densiteit = Column(Numeric(12, 6), nullable=True)
    min_ntu = Column(Numeric(12, 6), nullable=True)
    min_particulate_matter = Column(Numeric(12, 6), nullable=True)
    min_kleur = Column(Numeric(12, 6), nullable=True)
    min_so3 = Column(Numeric(12, 6), nullable=True)
    min_so2 = Column(Numeric(12, 6), nullable=True)
    min_cl = Column(Numeric(12, 6), nullable=True)
    min_nox = Column(Numeric(12, 6), nullable=True)
    min_po4 = Column(Numeric(12, 6), nullable=True)
    min_kristallisatie = Column(Numeric(12, 6), nullable=True)
    min_residu = Column(Numeric(12, 6), nullable=True)
    
    # Trace elements - minimum values
    min_fe = Column(Numeric(12, 6), nullable=True)
    min_cr = Column(Numeric(12, 6), nullable=True)
    min_ni = Column(Numeric(12, 6), nullable=True)
    min_as = Column(Numeric(12, 6), nullable=True)
    min_ba = Column(Numeric(12, 6), nullable=True)
    min_ca = Column(Numeric(12, 6), nullable=True)
    min_na = Column(Numeric(12, 6), nullable=True)
    min_al = Column(Numeric(12, 6), nullable=True)
    min_cd = Column(Numeric(12, 6), nullable=True)
    min_cu = Column(Numeric(12, 6), nullable=True)
    min_k = Column(Numeric(12, 6), nullable=True)
    min_mg = Column(Numeric(12, 6), nullable=True)
    min_pb = Column(Numeric(12, 6), nullable=True)
    min_hg = Column(Numeric(12, 6), nullable=True)
    min_zn = Column(Numeric(12, 6), nullable=True)
    min_sb = Column(Numeric(12, 6), nullable=True)
    min_v = Column(Numeric(12, 6), nullable=True)
    min_se = Column(Numeric(12, 6), nullable=True)
    min_li = Column(Numeric(12, 6), nullable=True)
    min_be = Column(Numeric(12, 6), nullable=True)
    min_b = Column(Numeric(12, 6), nullable=True)
    min_in = Column(Numeric(12, 6), nullable=True)
    min_sn = Column(Numeric(12, 6), nullable=True)
    min_ta = Column(Numeric(12, 6), nullable=True)
    min_au = Column(Numeric(12, 6), nullable=True)
    min_tl = Column(Numeric(12, 6), nullable=True)
    min_bi = Column(Numeric(12, 6), nullable=True)
    min_ti = Column(Numeric(12, 6), nullable=True)
    min_mn = Column(Numeric(12, 6), nullable=True)
    min_co = Column(Numeric(12, 6), nullable=True)
    min_ga = Column(Numeric(12, 6), nullable=True)
    min_sr = Column(Numeric(12, 6), nullable=True)
    min_zr = Column(Numeric(12, 6), nullable=True)
    min_nb = Column(Numeric(12, 6), nullable=True)
    min_mo = Column(Numeric(12, 6), nullable=True)
    min_ge = Column(Numeric(12, 6), nullable=True)
    min_h2so4 = Column(Numeric(12, 6), nullable=True)
    min_hso4 = Column(Numeric(12, 6), nullable=True)
    
    # Chemical limits - maximum values
    max_conc = Column(Numeric(12, 6), nullable=True)
    max_free_so3 = Column(Numeric(12, 6), nullable=True)
    max_free_hcl = Column(Numeric(12, 6), nullable=True)
    max_ph = Column(Numeric(12, 6), nullable=True)
    max_nh3 = Column(Numeric(12, 6), nullable=True)
    max_ats = Column(Numeric(12, 6), nullable=True)
    max_densiteit = Column(Numeric(12, 6), nullable=True)
    max_ntu = Column(Numeric(12, 6), nullable=True)
    max_particulate_matter = Column(Numeric(12, 6), nullable=True)
    max_kleur = Column(Numeric(12, 6), nullable=True)
    max_so3 = Column(Numeric(12, 6), nullable=True)
    max_so2 = Column(Numeric(12, 6), nullable=True)
    max_cl = Column(Numeric(12, 6), nullable=True)
    max_nox = Column(Numeric(12, 6), nullable=True)
    max_po4 = Column(Numeric(12, 6), nullable=True)
    max_kristallisatie = Column(Numeric(12, 6), nullable=True)
    max_residu = Column(Numeric(12, 6), nullable=True)
    
    # Trace elements - maximum values
    max_fe = Column(Numeric(12, 6), nullable=True)
    max_cr = Column(Numeric(12, 6), nullable=True)
    max_ni = Column(Numeric(12, 6), nullable=True)
    max_as = Column(Numeric(12, 6), nullable=True)
    max_ba = Column(Numeric(12, 6), nullable=True)
    max_ca = Column(Numeric(12, 6), nullable=True)
    max_na = Column(Numeric(12, 6), nullable=True)
    max_al = Column(Numeric(12, 6), nullable=True)
    max_cd = Column(Numeric(12, 6), nullable=True)
    max_cu = Column(Numeric(12, 6), nullable=True)
    max_k = Column(Numeric(12, 6), nullable=True)
    max_mg = Column(Numeric(12, 6), nullable=True)
    max_pb = Column(Numeric(12, 6), nullable=True)
    max_hg = Column(Numeric(12, 6), nullable=True)
    max_zn = Column(Numeric(12, 6), nullable=True)
    max_sb = Column(Numeric(12, 6), nullable=True)
    max_v = Column(Numeric(12, 6), nullable=True)
    max_se = Column(Numeric(12, 6), nullable=True)
    max_li = Column(Numeric(12, 6), nullable=True)
    max_be = Column(Numeric(12, 6), nullable=True)
    max_b = Column(Numeric(12, 6), nullable=True)
    max_in = Column(Numeric(12, 6), nullable=True)
    max_sn = Column(Numeric(12, 6), nullable=True)
    max_ta = Column(Numeric(12, 6), nullable=True)
    max_au = Column(Numeric(12, 6), nullable=True)
    max_tl = Column(Numeric(12, 6), nullable=True)
    max_bi = Column(Numeric(12, 6), nullable=True)
    max_ti = Column(Numeric(12, 6), nullable=True)
    max_mn = Column(Numeric(12, 6), nullable=True)
    max_co = Column(Numeric(12, 6), nullable=True)
    max_ga = Column(Numeric(12, 6), nullable=True)
    max_sr = Column(Numeric(12, 6), nullable=True)
    max_zr = Column(Numeric(12, 6), nullable=True)
    max_nb = Column(Numeric(12, 6), nullable=True)
    max_mo = Column(Numeric(12, 6), nullable=True)
    max_ge = Column(Numeric(12, 6), nullable=True)
    max_h2so4 = Column(Numeric(12, 6), nullable=True)
    max_hso4 = Column(Numeric(12, 6), nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="specs")
    quality = relationship("Quality", back_populates="specs")
    samples = relationship("Sample", back_populates="spec")
    spec_variables = relationship("SpecVariable", back_populates="spec")


class SpecVariable(BaseModel):
    """
    Specification variable detail model.

    Stores detailed variable-specific limits for specifications. This is a
    detail table that links specifications to variables with their specific
    min/max values, supporting dynamic specification configurations.

    Attributes:
        spec_id (int): Foreign key to specification table.
        variable_id (int): Foreign key to variable table.
        min_value (Decimal): Minimum acceptable value for this variable.
        max_value (Decimal): Maximum acceptable value for this variable.
    """
    __tablename__ = "dspec"
    
    spec_id = Column(Integer, ForeignKey("spec.id"), nullable=False)
    variable_id = Column(Integer, ForeignKey("variable.id"), nullable=False)
    min_value = Column(Numeric(12, 6), nullable=True)
    max_value = Column(Numeric(12, 6), nullable=True)
    
    # Relationships
    spec = relationship("Spec", back_populates="spec_variables")
    variable = relationship("Variable", back_populates="spec_variables")


class SampleMatrix(BaseModel):
    """
    Sample matrix configuration model.

    Defines which tests should be performed for specific product/quality/sample
    point combinations based on sampling frequency. Contains boolean flags for
    each possible test variable, allowing flexible test configuration.

    Attributes:
        product_id (int): Foreign key to product table.
        quality_id (int): Foreign key to quality table.
        sample_point_id (int): Foreign key to sample point table.
        spec_id (int): Foreign key to specification table.
        frequency (str): Sampling frequency - WEEK, MONTH, QUARTER, SEM (semester).
        has_* (bool): Boolean flags indicating which tests should be performed
            for various chemical parameters and trace elements (visual, conc,
            free_so3, ph, fe, cr, ni, as, etc.).

    Note:
        This model contains numerous has_* boolean fields that control which
        tests are active for a given product/quality/sample point combination.
    """
    __tablename__ = "samplematrix"
    
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quality_id = Column(Integer, ForeignKey("quality.id"), nullable=False)
    sample_point_id = Column(Integer, ForeignKey("samplepoint.id"), nullable=False)
    spec_id = Column(Integer, ForeignKey("spec.id"), nullable=False)
    frequency = Column(String(20), nullable=True)  # WEEK, MONTH, QUARTER, SEM
    
    # Boolean flags for each test variable
    has_visual = Column(Boolean, default=False)
    has_conc = Column(Boolean, default=False)
    has_free_so3 = Column(Boolean, default=False)
    has_ph = Column(Boolean, default=False)
    has_nh3 = Column(Boolean, default=False)
    has_ats = Column(Boolean, default=False)
    has_densiteit = Column(Boolean, default=False)
    has_ntu = Column(Boolean, default=False)
    has_particulate_matter = Column(Boolean, default=False)
    has_kleur = Column(Boolean, default=False)
    has_so3 = Column(Boolean, default=False)
    has_so2 = Column(Boolean, default=False)
    has_cl = Column(Boolean, default=False)
    has_nox = Column(Boolean, default=False)
    has_po4 = Column(Boolean, default=False)
    has_kristallisatie = Column(Boolean, default=False)
    has_residu = Column(Boolean, default=False)
    has_fe = Column(Boolean, default=False)
    has_cr = Column(Boolean, default=False)
    has_ni = Column(Boolean, default=False)
    has_as = Column(Boolean, default=False)
    has_ba = Column(Boolean, default=False)
    has_ca = Column(Boolean, default=False)
    has_na = Column(Boolean, default=False)
    has_al = Column(Boolean, default=False)
    has_cd = Column(Boolean, default=False)
    has_cu = Column(Boolean, default=False)
    has_k = Column(Boolean, default=False)
    has_mg = Column(Boolean, default=False)
    has_pb = Column(Boolean, default=False)
    has_hg = Column(Boolean, default=False)
    has_zn = Column(Boolean, default=False)
    has_sb = Column(Boolean, default=False)
    has_v = Column(Boolean, default=False)
    has_se = Column(Boolean, default=False)
    has_li = Column(Boolean, default=False)
    has_be = Column(Boolean, default=False)
    has_b = Column(Boolean, default=False)
    has_in = Column(Boolean, default=False)
    has_sn = Column(Boolean, default=False)
    has_ta = Column(Boolean, default=False)
    has_au = Column(Boolean, default=False)
    has_tl = Column(Boolean, default=False)
    has_bi = Column(Boolean, default=False)
    has_ti = Column(Boolean, default=False)
    has_mn = Column(Boolean, default=False)
    has_co = Column(Boolean, default=False)
    has_ga = Column(Boolean, default=False)
    has_sr = Column(Boolean, default=False)
    has_zr = Column(Boolean, default=False)
    has_nb = Column(Boolean, default=False)
    has_mo = Column(Boolean, default=False)
    has_ge = Column(Boolean, default=False)
    has_free_hcl = Column(Boolean, default=False)
    has_h2so4 = Column(Boolean, default=False)
    has_hso4 = Column(Boolean, default=False)
    
    # Relationships
    product = relationship("Product", back_populates="sample_matrices")
    quality = relationship("Quality", back_populates="sample_matrices")
    sample_point = relationship("SamplePoint", back_populates="sample_matrices")
    spec = relationship("Spec")
    samples = relationship("Sample", back_populates="sample_matrix")
    sample_matrix_variables = relationship("SampleMatrixVariable", back_populates="sample_matrix")


class SampleMatrixVariable(BaseModel):
    """
    Sample matrix variable detail model.

    Detail table that links sample matrices to specific variables, defining
    which variables should be tested for a given sample matrix configuration.

    Attributes:
        sample_matrix_id (int): Foreign key to sample matrix table.
        variable_id (int): Foreign key to variable table.
    """
    __tablename__ = "dsamplematrix"
    
    sample_matrix_id = Column(Integer, ForeignKey("samplematrix.id"), nullable=False)
    variable_id = Column(Integer, ForeignKey("variable.id"), nullable=False)
    
    # Relationships
    sample_matrix = relationship("SampleMatrix", back_populates="sample_matrix_variables")
    variable = relationship("Variable", back_populates="sample_matrix_variables")