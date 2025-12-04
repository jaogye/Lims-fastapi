"""
User and authentication database models module.

This module defines user management and authentication-related database models,
including User, OptionMenu, and UserOption for managing users, their permissions,
and menu access rights in the LIMS system.
"""

from sqlalchemy import Column, Integer, String, Boolean, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class User(BaseModel):
    """
    User model for system authentication and authorization.

    Stores user credentials, profile information, and digital signatures.
    Each user has a unique code, password hash, status, and administrative privileges.

    Attributes:
        code (str): Unique user code/username for login.
        name (str): Full name of the user.
        hashcode (str): Bcrypt password hash.
        status (bool): User account status (active/inactive).
        is_admin (bool): Administrative privileges flag.
        signature (bytes): Digital signature image in binary format.
        email (str): User's email address.
        temp_password (bool): Indicates if user must change their password on next login.
    """
    __tablename__ = "tuser"

    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    hashcode = Column(String(255), nullable=False)
    status = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    signature = Column(LargeBinary, nullable=True)
    email = Column(String(320), nullable=True)
    temp_password = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user_options = relationship("UserOption", foreign_keys="[UserOption.user_id]", back_populates="user")    
    created_samples = relationship("Sample", foreign_keys="[Sample.created_by_id]", back_populates="created_by")
    tested_measurements = relationship("Measurement", foreign_keys="[Measurement.tested_by_id]", back_populates="tested_by")


class OptionMenu(BaseModel):
    """
    Menu option model for defining available menu items.

    Defines available menu options and features in the system that can be
    assigned to users for access control.

    Attributes:
        name (str): Name of the menu option or feature.
    """
    __tablename__ = "optionmenu"

    name = Column(String(30), nullable=False)

    # Relationships
    user_options = relationship("UserOption", back_populates="option")


class UserOption(BaseModel):
    """
    User-option association model for menu permissions.

    Links users to their assigned menu options, defining which features
    and menu items each user can access. Implements many-to-many relationship
    between users and options.

    Attributes:
        user_id (int): Foreign key to user table.
        option_id (int): Foreign key to option menu table.
        hashcode (str): Optional hash code for additional security.
    """
    __tablename__ = "optionuser"
    
    user_id = Column(Integer, ForeignKey("tuser.id"), nullable=False, index=True)
    option_id = Column(Integer, ForeignKey("optionmenu.id"), nullable=False, index=True)
    hashcode = Column(String(60), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="user_options")
    option = relationship("OptionMenu", back_populates="user_options")