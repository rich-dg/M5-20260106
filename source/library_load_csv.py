import pandas as pd
import numpy as np
import logging
#import pyodbc
#import sqlalchemy as sa
import argparse

from pathlib import Path
from datetime import datetime

# Create SQLAlchemty connection, quick and dirty version using a simple string and windows auth.

#engine = sa.create_engine('mssql+pyodbc://localhost/QA_Library?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')
#connection = engine.connect()

# Declare variables & relative paths for consistency
today = pd.Timestamp.today()
script_dir = Path(__file__).parent
book_path = script_dir / '..' / 'data' / '03_Library Systembook.csv'
customer_path = script_dir / '..' / 'data' / '03_Library SystemCustomers.csv'

# Set up logging function
logging.addLevelName(25, "METRIC")

def metric(self, message, *args, **kwargs):
    """Metric logging"""
    if self.isEnabledFor(25):
        self._log(25, message, args, **kwargs)


logging.Logger.metric = metric

logger = logging.getLogger(__name__)

def setup_logging(log_dir):
    """Configure logging to file and console"""
    log_file = Path(log_dir) / f'library_etl_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    

    Path(log_dir).mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),  # Write to file
            logging.StreamHandler()          # Also print to console
        ]
    )
    
    logging.info(f"Logging to: {log_file}")
    return log_file

def standardise_columns(dataframe):
    """
    Cleans and standardises column names to snake_case
    
    Returns column names, not a dataframe
    """

    dataframe.columns = dataframe.columns.str.strip()\
                           .str.lower()\
                           .str.replace(" ", "_", regex=False)

    logger.info(f"Formated {len(dataframe.columns)} column headers.")
    return dataframe.columns

def clean_na(dataframe, columns):
    dataframe = dataframe.dropna(subset=columns)

    logger.info(f"Dropped NA values from {len(columns)} columns: {', '.join(columns)}")
    return dataframe


def format_date(dataframe, columns):
    for col in columns:
        before_format = dataframe[col].isnull().sum()
        dataframe[col] = pd.to_datetime(dataframe[col].str.strip('"\'',), format = '%d/%m/%Y', errors='coerce')
        after_format = dataframe[col].isnull().sum()
        format_fails = after_format - before_format
        logger.metric(f"Formated {col} date column: {format_fails} invalid dates")
    return dataframe


def format_id(dataframe, columns):
    for col in columns:
        dataframe[col] = dataframe[col].astype(int)

    logger.info(f"Formated {len(columns)} integer id's: {', '.join(columns)}")
    return dataframe


def format_names(dataframe, columns):
    for col in columns:
        dataframe[col] = dataframe[col].str.strip()\
                                       .str.title()
        
    logger.info(f"Formated {len(columns)} name columns: {', '.join(columns)}")
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
    logger.info("Date validator applied")
    return np.select(date_checks, date_flags, default="Valid dates")


def checkout_duration(dataframe, start_date, end_date, result_col, conditional_col=None, condition=None ):
    if (conditional_col is not None) & (condition is not None):
        duration = np.where(
            dataframe[conditional_col] == condition,
            (dataframe[end_date] - dataframe[start_date]).dt.days,
            pd.NaT
        )

    dataframe[result_col] = duration

    logger.info(f"Added [{result_col}] column: ({end_date} - {start_date}) where dates are valid")
    return dataframe


def write_table(dataframe, table_name, writeSQL, writeCSV):
#    if writeSQL == 1:
#        dataframe.to_sql(table_name, engine, if_exists='replace', index=False)
#        logging.info(f"the table [{table_name}] has been written the SQL Server")
    if writeCSV == 1:
        dataframe.to_csv(f"/library_data/{table_name}.csv")
        logging.info(f"the table [{table_name}] has been written to a CSV")
    else:
        return "No data has been saved"
    
def main():
    # Argparse input for toggling the SQL Server write.
    parser = argparse.ArgumentParser(prog = "LibraryCSV",
                                     description = "Loads CSV data to the SQL Server")
    parser.add_argument('-wsql', '--writeSQL', action='store_true', help="Writes the data to the SQL Server")
    parser.add_argument('-wcsv', '--writeCSV', action='store_true', help="Writes the data to a CSV")
    args = parser.parse_args()


    # Set up logging
    log_file = setup_logging('/library_data/logs')

    """
    Clean and load the book CSV
    """
    # Read CSV
    logger.info("Beginning book CSV processing.")
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
    #print(books_df)
    write_table(books_df, 'books', args.writeSQL, args.writeCSV)
    

    """
    Clean and load the customer CSV
    """

    # Read CSV
    logger.info("Beginning customer CSV processing.")
    customers_df = pd.read_csv(customer_path)

    # Standardise column headers
    customers_df.columns = standardise_columns(customers_df)

    # Clean data
    customers_df = clean_na(customers_df, ['customer_id'])
    customers_df = format_id(customers_df, ['customer_id'])
    customers_df = format_names(customers_df, ['customer_name'])

    # Display/Load the data
    #print(customers_df)
    write_table(customers_df, 'customers', args.writeSQL, args.writeCSV)

if __name__ == "__main__":
    main()
