"""
Logistic Data Loading Script

This script populates the logisticdata table with randomly generated test data
for customers, products, and orders spanning a date range.

Purpose:
    - Generate realistic test data for logistics operations
    - Populate the database with sample orders for testing and development
    - Create data entries with random customers, products, and tonnages
"""

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, event, text
from sqlalchemy.pool import NullPool
import random


from datetime import datetime, timedelta

def create_date_list(start_date, end_date):
    """
    Create a list of date strings from start_date to end_date.
    
    Args:
        start_date (str): Start date in 'yyyy-mm-dd' format
        end_date (str): End date in 'yyyy-mm-dd' format
    
    Returns:
        list: List of date strings in 'yyyy-mm-dd' format
    """
    # Convert strings to datetime objects
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Generate list of dates
    date_list = []
    current_date = start
    
    while current_date <= end:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    return date_list

# Example usage (commented out for production)
# dates = create_date_list('2024-01-01', '2024-01-10')
# print(dates)
# Output: ['2024-01-01', '2024-01-02', '2024-01-03', ..., '2024-01-10']

# ========================================
# Database Connection Setup
# ========================================
# Create database engine with SQL Server configuration
engine = create_engine(
    settings.database_url_sync,
    poolclass=NullPool,  # Use NullPool for SQL Server with pyodbc
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,   # Verify connections before use
    pool_recycle=3600,    # Recycle connections every hour
    connect_args={
        "check_same_thread": False,  # For SQLite compatibility if needed
        "timeout": 30,  # Connection timeout
    }
)

# Create session factory for database operations
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ========================================
# Data Preparation
# ========================================
# Initialize database session
db = SessionLocal()

# Fetch all customers from the customer table
tts = db.execute(text("SELECT customer from customer"))  # List of tuples
lst_customers = [t[0].strip() for t in tts]

# Fetch article codes and descriptions from product-quality mappings
tts = db.execute(text("""SELECT article_code, concat(trim(p.name),' ', trim(q.name)) description
                      FROM map m, product p, quality q
                      WHERE m.product_id=p.id and m.quality_id=q.id"""))  # List of tuples
lst_maps = [(t[0], t[1].strip()) for t in tts]

# Generate date range for test data (June 1 to December 31, 2025)
lst_dates = create_date_list('2025-06-01', '2025-12-31')

# Define typical loading times throughout the day
lst_times = ['06:00', '07:10', '08:12', '09:14', '12:23', '14:50', '16:15', '17:00']

# ========================================
# Data Generation
# ========================================
# Clear existing logistic data before generating new test data
result = db.execute(text("DELETE FROM logisticdata"))
db.commit()

# Generate random logistic data for each date
for date in lst_dates:
    print('date:', date)

    # Generate random number of orders for this date (between 10 and 50)
    n_tot = random.randint(10, 50)

    for _ in range(n_tot):
        # Randomly select a customer from the list
        customer = lst_customers[random.randint(0, len(lst_customers) - 1)]

        # Randomly select an article code and description
        article_code, description = lst_maps[random.randint(0, len(lst_maps) - 1)]

        # Randomly select a loading time
        time = lst_times[random.randint(0, len(lst_times) - 1)]

        # Create a row with random data
        row = {
            "date": date,
            "time": time,
            "customer": customer,
            "order1": random.randint(0, 50000),  # PVS order number
            "article_code": article_code,
            "order2": str(random.randint(0, 50000)),  # Client order number
            "description": description,
            "ton": random.randint(0, 10000) / 100  # Loading tonnage (0-100 tons)
        }

        # Insert the generated data into the logisticdata table
        insert = """INSERT into logisticdata( date,time, name_client,  ordernumber_PVS,  article_no,
                 ordernumber_client, Description, loading_ton) VALUES (:date, :time,
                 :customer, :order1, :article_code, :order2, :description, :ton)"""
        result = db.execute(text(insert), row)
        db.commit()


