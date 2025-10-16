from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine 

from app.core.config import settings
from app.models.user import User
from app.models.laboratory import Product, Quality, Variable, SamplePoint, Holidays
from app.models.specification import SampleMatrix
from app.models.sample import Map
import pandas as pd

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()
quality = db.query(Quality).all()


