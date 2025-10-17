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
tts = db.execute(text("""SELECT customer, product_id, quality_id, p.name product, q.name quality 
                      FROM spec s, product p, quality q
                      WHERE  s.type_spec='CLI' and s.product_id=p.id AND s.quality_id=q.id"""))  # List of tuples
lst_customerlist = [( t[0].strip(), t[1], t[2], t[3].strip(), t[4].strip() ) for t in tts]

# Fetch all customers from the customer table
tts = db.execute(text("""SELECT article_code, product_id, quality_id 
                      FROM map ORDER BY product_id, quality_id"""))  # List of tuples
lst_maps = [t for t in tts]
dict_maps = {}
for t in lst_maps:
    key = str(t[1]) + '_' + str(t[2])
    if not key in dict_maps:
        dict_maps[key] = []
    dict_maps[key].append( t[0] )


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
        customer, product_id, quality_id, product, quality = lst_customerlist[random.randint(0, len(lst_customerlist) - 1)]
        description = product + ' ' + quality
        # Randomly select an article code and description
        key = str(product_id) + '_' + str(quality_id)
        ll = dict_maps[key]
        article_code = ll[random.randint(0, len(ll) - 1)]
        
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
        insert = """INSERT into logisticdata( date,time, name_client,  order_number_PVS,  article_no,
                 order_number_client, Description, loading_ton) VALUES (:date, :time,
                 :customer, :order1, :article_code, :order2, :description, :ton)"""
        result = db.execute(text(insert), row)
        db.commit()


