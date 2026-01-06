import pandas as pd
import numpy as np
import pyodbc
import sqlalchemy as sa
from pathlib import Path

from datetime import datetime

# Create SQLAlchemty connection, quick and dirty version using a simple string and windows auth.

engine = sa.create_engine('mssql+pyodbc://localhost/QA_Library?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')
connection = engine.connect()

# Declare variables & relative paths for consistency
today = pd.Timestamp(datetime.today())

script_dir = Path(__file__).parent
book_path = script_dir / '..' / 'data' / '03_Library Systembook.csv'
customer_path = script_dir / '..' / 'data' / '03_Library SystemCustomers.csv'


"""
Clean and load the book CSV
"""

# Read CSV
books_df = pd.read_csv(book_path)

# Standardise column headers
books_df.columns = books_df.columns.str.title()

# Drops NaN records
books_df = books_df.dropna(subset=['Id', 'Books'])

# Convert Id fields to integers
for col in ['Id', 'Customer Id']:
    books_df[col] = books_df[col].astype(int)

# Capitalisew book titles
books_df['Books'] = books_df['Books'].str.title()

# Standardise dates
for col in ['Book Checkout', 'Book Returned']:
    books_df[col] = pd.to_datetime(books_df[col].str.strip('"'), format = '%d/%m/%Y', errors='coerce')

# Date validation
date_checks = [
    books_df['Book Checkout'].isna() | books_df['Book Returned'].isna(),
    (books_df['Book Checkout'] > today) | (books_df['Book Returned'] > today),
    books_df['Book Checkout'] > books_df['Book Returned']
]

date_flags = [
    'Invalid Dates',
    'Future Dates',
    'Checked Prceeding Return'
]

books_df['Date Validity'] = np.select(date_checks, date_flags, default='Valid Date')


# Calculate valid lending durations
books_df['Checkout Duration'] = np.where(
    books_df['Date Validity'] == 'Valid Date',
    (books_df['Book Returned'] - books_df['Book Checkout']).dt.days,
    None
)

# Load the data
books_df.to_sql('books', engine, if_exists='replace', index=False)


"""
Clean and load the customer CSV
"""

# Read CSV
customers_df = pd.read_csv(customer_path)

# Standardise column headers
customers_df.columns = customers_df.columns.str.title()

# Drops NaN records
customers_df = customers_df.dropna()

# Convert Id fields to integers
customers_df['Customer Id'] = customers_df['Customer Id'].astype(int)

# Standardise capitalisation
customers_df['Customer Name'] = customers_df['Customer Name'].str.title()

# Load the data
customers_df.to_sql('customers', engine, if_exists='replace', index=False)

