import pandas as pd
import numpy as np
import pyodbc
import sqlalchemy as sa
import argparse

from pathlib import Path
from datetime import datetime

# Create SQLAlchemty connection, quick and dirty version using a simple string and windows auth.

engine = sa.create_engine('mssql+pyodbc://localhost/QA_Library?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')
connection = engine.connect()

# Declare variables & relative paths for consistency
today = pd.Timestamp.today()
script_dir = Path(__file__).parent
book_path = script_dir / '..' / 'data' / '03_Library Systembook.csv'
customer_path = script_dir / '..' / 'data' / '03_Library SystemCustomers.csv'

def standardise_columns(dataframe):
    """
    Cleans and standardises column names to snake_case
    
    Returns column names, not a dataframe
    """

    dataframe.columns = dataframe.columns.str.strip()\
                           .str.lower()\
                           .str.replace(" ", "_", regex=False)

    print(f"Formated {len(dataframe.columns)} column headers.")
    return dataframe.columns

def clean_na(dataframe, columns):
    dataframe = dataframe.dropna(subset=columns)

    print(f"Dropped NA values from {len(columns)} columns: {', '.join(columns)}")
    return dataframe


def format_date(dataframe, columns):
    for col in columns:
        dataframe[col] = pd.to_datetime(dataframe[col].str.strip('"'), format = '%d/%m/%Y', errors='coerce')

    print(f"Formated {len(columns)} date columns: {', '.join(columns)}")
    return dataframe


def format_id(dataframe, columns):
    for col in columns:
        dataframe[col] = dataframe[col].astype(int)

    print(f"Formated {len(columns)} integer id's: {', '.join(columns)}")
    return dataframe


def format_names(dataframe, columns):
    for col in columns:
        dataframe[col] = dataframe[col].str.strip()\
                                       .str.title()
        
    print(f"Formated {len(columns)} name columns: {', '.join(columns)}")
    return dataframe


def date_validator(checkout_series, returned_series):
    """
    Date Validator returning a string classification
    """
    
    today = pd.Timestamp.today()
    
    date_checks = [
        checkout_series.isna() | returned_series.isna(),
        (checkout_series > today) | (returned_series > today),
        checkout_series > returned_series
    ]
    
    date_flags = [
        "Invalid dates",
        "Future dates",
        "Checkout preceding return"
    ]
    print("Date validator applied")
    return np.select(date_checks, date_flags, default="Valid dates")


def checkout_duration(dataframe, start_date, end_date, result_col, conditional_col=None, condition=None ):
    if (conditional_col is not None) & (condition is not None):
        duration = np.where(
            dataframe[conditional_col] == condition,
            (dataframe[end_date] - dataframe[start_date]).dt.days,
            pd.NaT
        )

    dataframe[result_col] = duration

    print(f"Added [{result_col}] column: ({end_date} - {start_date}) where dates are valid")
    return dataframe


def write_table(dataframe, table_name, write_toggle):
    if write_toggle == 1:
        dataframe.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"the table [{table_name}] has been written the SQL Server")
    else:
        return "No data has been saved"
    
def main():
    # Argparse input for toggling the SQL Server write.
    parser = argparse.ArgumentParser(prog = "LibraryCSV",
                                     description = "Loads CSV data to the SQL Server")
    parser.add_argument('-w', '--write', action='store_true', help="Writes the data to the SQL Server")
    args = parser.parse_args()

    """
    Clean and load the book CSV
    """
    # Read CSV
    books_df = pd.read_csv(book_path)

    # Standardise column headers
    books_df.columns = standardise_columns(books_df)

    # Clean data
    books_df = clean_na(books_df, ['id', 'customer_id'])
    books_df = format_id(books_df, ['id', 'customer_id'])
    books_df = format_names(books_df, ['books'])
    books_df = format_date(books_df,['book_checkout', 'book_returned'])

    # Enrich Data
    books_df['date_validity'] = date_validator(books_df['book_checkout'], books_df['book_returned'])
    books_df = checkout_duration(books_df, 
                                 'book_checkout', 
                                 'book_returned', 
                                 'checkout_duration', 
                                 'date_validity', 
                                 "Valid dates")

    # Display/Load the data
    print(books_df)
    write_table(books_df, 'books', args.write)
    

    """
    Clean and load the customer CSV
    """

    # Read CSV
    customers_df = pd.read_csv(customer_path)

    # Standardise column headers
    customers_df.columns = standardise_columns(customers_df)

    # Clean data
    customers_df = clean_na(customers_df, ['customer_id'])
    customers_df = format_id(customers_df, ['customer_id'])
    customers_df = format_names(customers_df, ['customer_name'])

    # Display/Load the data
    print(customers_df)
    write_table(customers_df, 'customers', args.write)

if __name__ == "__main__":
    main()
